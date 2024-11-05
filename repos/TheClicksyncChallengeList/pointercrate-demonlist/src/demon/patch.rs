use crate::{
    demon::{Demon, FullDemon, MinimalDemon},
    error::{DemonlistError, Result},
    player::{recompute_scores, DatabasePlayer},
};
use log::{debug, info, warn};
use pointercrate_core::util::{non_nullable, nullable};
use serde::Deserialize;
use sqlx::PgConnection;

#[derive(Deserialize, Debug, Default)]
pub struct PatchDemon {
    #[serde(default, deserialize_with = "non_nullable")]
    pub name: Option<String>,

    #[serde(default, deserialize_with = "non_nullable")]
    pub position: Option<i16>,

    #[serde(default, deserialize_with = "nullable")]
    pub video: Option<Option<String>>,

    #[serde(default, deserialize_with = "non_nullable")]
    pub thumbnail: Option<String>,

    #[serde(default, deserialize_with = "non_nullable")]
    pub requirement: Option<i16>,

    #[serde(default, deserialize_with = "non_nullable")]
    pub verifier: Option<String>,

    #[serde(default, deserialize_with = "non_nullable")]
    pub publisher: Option<String>,

    #[serde(default, deserialize_with = "non_nullable")]
    pub level_id: Option<u64>,
}

impl FullDemon {
    pub async fn apply_patch(mut self, patch: PatchDemon, connection: &mut PgConnection) -> Result<Self> {
        let changes_requirement = patch.requirement.is_some();

        let updated_demon = self.demon.apply_patch(patch, connection).await?;

        if changes_requirement {
            self.records.retain(|record| record.progress >= updated_demon.requirement);
        }

        Ok(FullDemon {
            demon: updated_demon,
            ..self
        })
    }
}

impl Demon {
    /// Must run inside a transaction!
    pub async fn apply_patch(mut self, patch: PatchDemon, connection: &mut PgConnection) -> Result<Self> {
        // duplicate names are OK nowadays

        if let Some(position) = patch.position {
            self.base.mv(position, connection).await?;
        }

        if let Some(name) = patch.name {
            self.base.set_name(name, connection).await?;
        }

        if let Some(video) = patch.video {
            match video {
                None => self.remove_video(connection).await?,
                Some(video) => self.set_video(video, connection).await?,
            }
        }

        if let Some(thumbnail) = patch.thumbnail {
            self.set_thumbnail(thumbnail, connection).await?;
        }

        if let Some(verifier) = patch.verifier {
            let player = DatabasePlayer::by_name_or_create(verifier.as_ref(), connection).await?;

            self.set_verifier(player, connection).await?;
        }

        if let Some(publisher) = patch.publisher {
            let player = DatabasePlayer::by_name_or_create(publisher.as_ref(), connection).await?;

            self.set_publisher(player, connection).await?;
        }

        if let Some(requirement) = patch.requirement {
            self.set_requirement(requirement, connection).await?;
        }
        if let Some(level_id) = patch.level_id {
            self.set_level_id(level_id as i64, connection).await?;
        }

        Ok(self)
    }

    pub async fn set_verifier(&mut self, verifier: DatabasePlayer, connection: &mut PgConnection) -> Result<()> {
        if verifier.id != self.verifier.id {
            sqlx::query!("UPDATE demons SET verifier = $1 WHERE id = $2", verifier.id, self.base.id)
                .execute(&mut *connection)
                .await?;

            self.verifier.update_score(connection).await?;
            verifier.update_score(connection).await?;

            self.verifier = verifier;
        }

        Ok(())
    }

    pub async fn set_publisher(&mut self, publisher: DatabasePlayer, connection: &mut PgConnection) -> Result<()> {
        if publisher.id != self.publisher.id {
            sqlx::query!("UPDATE demons SET publisher = $1 WHERE id = $2", publisher.id, self.base.id)
                .execute(connection)
                .await?;

            self.publisher = publisher;
        }

        Ok(())
    }

    pub async fn set_requirement(&mut self, requirement: i16, connection: &mut PgConnection) -> Result<()> {
        if !(0..=100).contains(&requirement) {
            return Err(DemonlistError::InvalidRequirement);
        }

        // Delete associated notes
        sqlx::query!("DELETE FROM records WHERE demon = $1 AND progress < $2", self.base.id, requirement)
            .execute(&mut *connection)
            .await?;

        sqlx::query!("UPDATE demons SET requirement = $1 WHERE id = $2", requirement, self.base.id)
            .execute(connection)
            .await?;

        self.requirement = requirement;

        Ok(())
    }

    pub async fn set_video(&mut self, video: String, connection: &mut PgConnection) -> Result<()> {
        let video = crate::video::validate(&video)?;

        sqlx::query!("UPDATE demons SET video = $1::text WHERE id = $2", video, self.base.id)
            .execute(connection)
            .await?;

        self.video = Some(video);

        Ok(())
    }

    pub async fn remove_video(&mut self, connection: &mut PgConnection) -> Result<()> {
        sqlx::query!("UPDATE demons SET video = NULL WHERE id = $1", self.base.id)
            .execute(connection)
            .await?;

        self.video = None;

        Ok(())
    }

    pub async fn set_thumbnail(&mut self, thumbnail: String, connection: &mut PgConnection) -> Result<()> {
        sqlx::query!("UPDATE demons SET thumbnail = $1::text WHERE id = $2", thumbnail, self.base.id)
            .execute(connection)
            .await?;

        self.thumbnail = thumbnail;

        Ok(())
    }
    pub async fn set_level_id(&mut self, level_id: i64, connection: &mut PgConnection) -> Result<()> {
        sqlx::query!("UPDATE demons SET level_id = $1 WHERE id = $2", level_id, self.base.id)
            .execute(connection)
            .await?;

        self.level_id = Some(level_id as u64);

        Ok(())
    }
}

impl MinimalDemon {
    pub async fn set_name(&mut self, name: String, connection: &mut PgConnection) -> Result<()> {
        if self.name != name {
            sqlx::query!("UPDATE demons SET name = $1::text WHERE id = $2", name.to_string(), self.id)
                .execute(connection)
                .await?;

            self.name = name
        }

        Ok(())
    }

    /// Moves this demon to the specified position
    ///
    /// Validates that `to` is `> 0` and less than or equal to the currently highest position on the
    /// list (to preven "holes")
    pub async fn mv(&mut self, to: i16, connection: &mut PgConnection) -> Result<()> {
        // This returns 0 if the list is empty, but if the list is empty then there is no demon for us to do a move with, so we will never get here anyway.
        let maximal_position = Demon::max_position(connection).await?;

        if to > maximal_position || to < 1 {
            return Err(DemonlistError::InvalidPosition { maximal: maximal_position });
        }

        if to == self.position {
            warn!("No-op move of demon {}", self);

            return Ok(());
        }

        // FIXME: Temporarily move the demon somewhere else because otherwise the unique constraints
        // complains. I actually dont know why, its DEFERRABLE INITIALLY IMMEDIATE (whatever
        // that means, it made it work in the python version of the demonlist)
        sqlx::query!("UPDATE demons SET position = -1 WHERE id = $1", self.id)
            .execute(&mut *connection)
            .await?;

        if to > self.position {
            debug!(
                "Target position {} is greater than current position {}, shifting demons towards lower position",
                to, self.position
            );

            sqlx::query!(
                "UPDATE demons SET position = position - 1 WHERE position > $1 AND position <= $2",
                self.position,
                to
            )
            .execute(&mut *connection)
            .await?;
        } else if to < self.position {
            debug!(
                "Target position {} is lesser than current position {}, shifting demons towards higher position",
                to, self.position
            );

            sqlx::query!(
                "UPDATE demons SET position = position + 1 WHERE position >= $1 AND position < $2",
                to,
                self.position
            )
            .execute(&mut *connection)
            .await?;
        }

        debug!("Performing actual move to position {}", to);

        sqlx::query!("UPDATE demons SET position = $2 WHERE id = $1", self.id, to)
            .execute(&mut *connection)
            .await?;

        info!("Moved demon {} from {} to {} successfully!", self, self.position, to);

        self.position = to;

        recompute_scores(connection).await?;

        Ok(())
    }
}
