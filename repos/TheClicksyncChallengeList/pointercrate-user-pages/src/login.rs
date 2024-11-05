use maud::{html, Markup};
use pointercrate_core_pages::{head::HeadLike, PageFragment};

pub fn login_page() -> PageFragment {
    PageFragment::new(
        "Pointercrate - Login",
        "Log in to an existing pointercrate account or register for a new one!",
    )
    .module("/static/user/js/login.js")
    .module("/static/core/js/modules/form.js")
    .stylesheet("/static/user/css/login.css")
    .body(login_page_body())
}

fn login_page_body() -> Markup {
    let legacy_register = if cfg!(feature = "legacy_accounts") {
        html! {
            div.flex.col {
                h2 {"Register"}
                p {
                    "Not registered yet? Create a new pointercrate account below."
                }
                form.flex.col.grow #register-form novalidate = "" {
                    p.info-red.output {}
                    span.form-input #register-username {
                        label for = "name" {"Username:"}
                        input required = "" type = "text" name = "name";
                        p.error {}
                    }
                    span.form-input #register-password {
                        label for = "password" {"Password:"}
                        input required = "" type = "password" name = "password" minlength = "10";
                        p.error {}
                    }
                    span.form-input #register-password-repeat {
                        label for = "password2" {"Repeat Password:"}
                        input required = "" type = "password" name = "password2" minlength = "10";
                        p.error {}
                    }
                    div.grow {}
                    input.button.blue.hover type = "submit" style = "margin: 15px auto 0px;" value = "Register";
                }
            }
        }
    } else {
        html!()
    };
    html! {
        div.m-center.flex.panel.fade.col.wrap style = "margin: 100px 0px;"{
            h1.underlined.pad {
                "Pointercrate Account"
            }
            p {
                "By using pointercrate accounts you agree to cookies. If you don't then I formally request you to stop using the internet as you obviously have no idea what you're talking about. "
            }
            div.flex #login {
                div.flex.col {
                    h2 {"Login"}
                    p {
                        "Log in to an existing pointercrate account. You have 3 login attempts every 30 minutes. If you do not have an account yet, register on the right or below. "
                    }
                    form.flex.col.grow #login-form novalidate = "" {
                        p.info-red.output {}
                        span.form-input #login-username {
                            label for = "username" {"Username:"}
                            input required = "" type = "text" name = "username" minlength = "3";
                            p.error {}
                        }
                        span.form-input #login-password {
                            label for = "password" {"Password:"}
                            input required = "" type = "password" name = "password" minlength = "10";
                            p.error {}
                        }
                        div.grow {}
                        input.button.blue.hover type = "submit" style = "margin: 15px auto 0px;" value="Log in";
                    }
                }
                (legacy_register)
            }
        }
    }
}
