use crate::ratelimits::DemonlistRatelimits;
use pointercrate_core::{audit::AuditLogEntry, pool::PointercratePool};
use pointercrate_core_api::{
    error::Result,
    etag::{Precondition, TaggableExt, Tagged},
    pagination::pagination_response,
    query::Query,
    response::Response2,
};
use pointercrate_demonlist::{
    creator::{Creator, PostCreator},
    demon::{
        audit::{DemonModificationData, MovementLogEntry},
        Demon, DemonIdPagination, DemonPositionPagination, FullDemon, PatchDemon, PostDemon,
    },
    error::DemonlistError,
    player::{recompute_scores, DatabasePlayer},
    LIST_ADMINISTRATOR, LIST_MODERATOR,
};
use pointercrate_user::auth::ApiToken;
use pointercrate_user_api::auth::Auth;
use rocket::{http::Status, serde::json::Json, State};

#[rocket::get("/")]
pub async fn paginate(pool: &State<PointercratePool>, pagination: Query<DemonIdPagination>) -> Result<Response2<Json<Vec<Demon>>>> {
    Ok(pagination_response("/api/v2/demons/", pagination.0, &mut *pool.connection().await?).await?)
}

#[rocket::get("/listed")]
pub async fn paginate_listed(
    pool: &State<PointercratePool>, pagination: Query<DemonPositionPagination>,
) -> Result<Response2<Json<Vec<Demon>>>> {
    Ok(pagination_response("/api/v2/demons/listed/", pagination.0, &mut *pool.connection().await?).await?)
}

#[rocket::get("/<demon_id>")]
pub async fn get(demon_id: i32, pool: &State<PointercratePool>) -> Result<Tagged<FullDemon>> {
    Ok(Tagged(FullDemon::by_id(demon_id, &mut *pool.connection().await?).await?))
}

#[rocket::get("/<demon_id>/audit")]
pub async fn audit(demon_id: i32, mut auth: Auth<ApiToken>) -> Result<Json<Vec<AuditLogEntry<DemonModificationData>>>> {
    auth.require_permission(LIST_ADMINISTRATOR)?;

    let log = pointercrate_demonlist::demon::audit::audit_log_for_demon(demon_id, &mut auth.connection).await?;

    if log.is_empty() {
        return Err(DemonlistError::DemonNotFound { demon_id }.into());
    }

    Ok(Json(log))
}

#[rocket::get("/<demon_id>/audit/movement")]
pub async fn movement_log(demon_id: i32, pool: &State<PointercratePool>) -> Result<Json<Vec<MovementLogEntry>>> {
    let log = pointercrate_demonlist::demon::audit::movement_log_for_demon(demon_id, &mut *pool.connection().await?).await?;

    if log.is_empty() {
        return Err(DemonlistError::DemonNotFound { demon_id }.into());
    }

    Ok(Json(log))
}

#[rocket::post("/", data = "<data>")]
pub async fn post(
    mut auth: Auth<ApiToken>, data: Json<PostDemon>, ratelimits: &State<DemonlistRatelimits>,
) -> Result<Response2<Tagged<FullDemon>>> {
    auth.require_permission(LIST_MODERATOR)?;

    ratelimits.add_demon()?;

    let demon = FullDemon::create_from(data.0, &mut auth.connection).await?;

    auth.commit().await?;

    let demon_id = demon.demon.base.id;

    Ok(Response2::tagged(demon)
        .status(Status::Created)
        .with_header("Location", format!("/api/v2/demons/{}/", demon_id)))
}

#[rocket::patch("/<demon_id>", data = "<patch>")]
pub async fn patch(
    demon_id: i32, mut auth: Auth<ApiToken>, precondition: Precondition, patch: Json<PatchDemon>,
) -> Result<Tagged<FullDemon>> {
    auth.require_permission(LIST_MODERATOR)?;

    let demon = FullDemon::by_id(demon_id, &mut auth.connection)
        .await?
        .require_match(precondition)?
        .apply_patch(patch.0, &mut auth.connection)
        .await?;

    auth.commit().await?;

    Ok(Tagged(demon))
}

#[rocket::post("/<demon_id>/creators", data = "<creator>")]
pub async fn post_creator(demon_id: i32, mut auth: Auth<ApiToken>, creator: Json<PostCreator>) -> Result<Response2<Json<()>>> {
    auth.require_permission(LIST_MODERATOR)?;

    let demon = Demon::by_id(demon_id, &mut auth.connection).await?;
    let player = DatabasePlayer::by_name_or_create(&creator.creator, &mut auth.connection).await?;

    Creator::insert(&demon.base, &player, &mut auth.connection).await?;

    auth.commit().await?;

    Ok(Response2::json(()).status(Status::Created).with_header(
        "Location",
        format!("/api/v2/demons/{}/creators/{}/", demon.base.position, player.id),
    ))
}

#[rocket::delete("/<demon_id>/creators/<player_id>")]
pub async fn delete_creator(demon_id: i32, player_id: i32, mut auth: Auth<ApiToken>) -> Result<Status> {
    auth.require_permission(LIST_MODERATOR)?;

    let demon = Demon::by_id(demon_id, &mut auth.connection).await?;
    let player = DatabasePlayer::by_id(player_id, &mut auth.connection).await?;

    Creator::get(&demon.base, &player, &mut auth.connection)
        .await?
        .delete(&mut auth.connection)
        .await?;

    auth.commit().await?;

    Ok(Status::NoContent)
}

#[rocket::delete("/<demon_id>")]

/// delete all creators and records from a demon, and delete the demon itself
pub async fn delete_demon_data(demon_id: i32, mut auth: Auth<ApiToken>) -> Result<Status> {
    auth.require_permission(LIST_MODERATOR)?;

    // pass in the id of the demon we're trying to delete
    let demon = FullDemon::by_id(demon_id, &mut auth.connection).await?;

    // we don't really need fulldemon here but oh well
    FullDemon::by_id(demon.demon.base.id, &mut auth.connection)
        .await?
        .delete_demon(&mut auth.connection)
        .await?;

    recompute_scores(&mut auth.connection).await?;

    auth.commit().await?;

    Ok(Status::NoContent)
}
