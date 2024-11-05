use maud::{html, Markup};

use pointercrate_demonlist::{config, demon::Demon};

pub mod account;
pub mod components;
pub mod demon_page;
pub mod overview;
pub mod statsviewer;

struct ListSection {
    name: &'static str,
    description: &'static str,
    id: &'static str,
    numbered: bool,
}

static MAIN_SECTION: ListSection = ListSection {
    name: "Search for a challenge here!",
    description: "",
    id: "mainlist",
    numbered: true,
};

/* static EXTENDED_SECTION: ListSection = ListSection {
    name: "Extended List",
    description: "These are demons that dont qualify for the main section of the list, but are still of high relevance. Only 100% records \
                  are accepted for these demons! Note that non-100% that were submitted/approved before a demon fell off the main list \
                  will be retained",
    id: "extended",
    numbered: true,
};

static LEGACY_SECTION: ListSection = ListSection {
    name: "Legacy List",
    description: "These are demons that used to be on the list, but got pushed off as new demons were added. They are here for nostalgic \
                  reasons. This list is in no order whatsoever and will not be maintained any longer at all. This means no new records \
                  will be added for these demons.",
    id: "legacy",
    numbered: false,
};
*/

fn dropdowns(all_demons: &[&Demon], current: Option<&Demon>) -> Markup {
    let (main, extended, legacy) = if all_demons.len() < config::list_size() as usize {
        (all_demons, Default::default(), Default::default())
    } else {
        let (extended, legacy) = if all_demons.len() < config::extended_list_size() as usize {
            (&all_demons[config::list_size() as usize..], Default::default())
        } else {
            (
                &all_demons[config::list_size() as usize..config::extended_list_size() as usize],
                &all_demons[config::extended_list_size() as usize..],
            )
        };

        (&all_demons[..config::list_size() as usize], extended, legacy)
    };

    html! {
        nav.flex.wrap.m-center.fade #lists style="text-align: center;" {
             // The drop down for the main list:
            (dropdown(&MAIN_SECTION, main, current))
            // The drop down for the extended list:
            /*
            (dropdown(&EXTENDED_SECTION, extended, current))
            // The drop down for the legacy list:
            (dropdown(&LEGACY_SECTION, legacy, current))
            */
        }
    }
}

fn dropdown(section: &ListSection, demons: &[&Demon], current: Option<&Demon>) -> Markup {
    let format = |demon: &Demon| -> Markup {
        html! {
            a href = {"/list/permalink/" (demon.base.id) "/"} {
                @if section.numbered {
                    {"#" (demon.base.position) " - " (demon.base.name)}
                    br ;
                    i {
                        (demon.publisher.name)
                    }
                }
                @else {
                    {(demon.base.name)}
                    br ;
                    i {
                        (demon.publisher.name)
                    }
                }
            }
        }
    };

    html! {
        div {
            div.button.white.hover.no-shadow.js-toggle data-toggle-group="0" onclick={"javascript:void(DropDown.toggleDropDown('" (section.id) "'))"} {
                (section.name)
            }

            div.see-through.fade.dropdown #(section.id) {
                div.search.js-search.seperated style = "margin: 10px" {
                    input type = "text" {}
                }
                p style = "margin: 10px" {
                    (section.description)
                }
                ul.flex.wrap.space {
                    @for demon in demons {
                        @match current {
                            Some(current) if current.base.position == demon.base.position =>
                                li.hover.white.active title={"#" (demon.base.position) " - " (demon.base.name)} {
                                    (format(demon))
                                },
                            _ =>
                                li.hover.white title={"#" (demon.base.position) " - " (demon.base.name)} {
                                    (format(demon))
                                }
                        }
                    }
                }
            }
        }
    }
}

fn rules_panel() -> Markup {
    html! {
        section #rules.panel.fade.js-scroll-anim data-anim = "fade" {
            h2.underlined.pad.clickable {
                "Guidelines"
            }
            p {
                "Read this before submitting a challenge or record to ensure a flawless experience."
            }
            a.blue.hover.button href = "https://docs.google.com/document/d/1zW2tOWRi-qTxd2pM2FrParnVTzJjzRiGKIGGSJycKuI/edit?usp=sharing" {
                "Read the guidelines!"
            }
        }
    }
}

fn nongs_panel() -> Markup {
    html! {
        section #rules.panel.fade.js-scroll-anim data-anim = "fade" {
            h2.underlined.pad.clickable {
                "Nongs"
            }
            p {
                "Some challenges have songs that aren't on " a.link href = {"https://www.newgrounds.com"} {"Newgrounds"} ", so you can find all NONG songs in this Google Drive folder."
            }
            a.blue.hover.button href = "https://drive.google.com/drive/folders/1_P5D7jKT8oUcjk_vzWt5riqouOnnwRqB?usp=sharing" {
                "Find a nong!"
            }
        }
    }
}
