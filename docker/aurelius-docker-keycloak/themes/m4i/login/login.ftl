<#import "template.ftl" as layout>
<@layout.registrationLayout displayInfo=social.displayInfo displayWide=(realm.password && social.providers??); section>
    <#if section = "header">
        ${msg("doLogIn")}
    <#elseif section = "form">
    <div id="kc-form">
      <div id="kc-form-wrapper">
        <#if realm.password>
            <form id="kc-form-login" onsubmit="login.disabled = true; return true;" action="${url.loginAction}" method="post">
                <div class="field">
                    <label class="label" for="username"><#if !realm.loginWithEmailAllowed>${msg("username")}<#elseif !realm.registrationEmailAsUsername>${msg("usernameOrEmail")}<#else>${msg("email")}</#if></label>
                    <p class="control has-icons-left is-expanded">
                        <#if usernameEditDisabled??>
                            <input class="input" id="username" name="username" value="${(login.username!'')}" type="text" disabled />
                        <#else>
                            <input class="input" id="username" name="username" value="${(login.username!'')}"  type="text" autofocus autocomplete="off" />
                        </#if>
                        <span class="icon is-small is-left">
                            <i class="fas fa-user"></i>
                        </span>
                    </p>
                </div>
                <div class="field">
                    <label class="label" for="password">${msg("password")}</label>
                    <p class="control has-icons-left is-expanded">
                        <input class="input" id="password" name="password" type="password" autocomplete="off" />
                        <span class="icon is-small is-left">
                            <i class="fas fa-key"></i>
                        </span>
                    </p>
                </div>
                <hr class="hr">
                <div id="kc-form-options">
                    <#if realm.rememberMe && !usernameEditDisabled??>
                        <div class="field" style="margin-bottom: 0.75rem">
                            <#if login.rememberMe??>
                                <input class="is-checkradio" id="rememberMe" name="rememberMe" type="checkbox" checked>
                            <#else>
                                <input class="is-checkradio" id="rememberMe" name="rememberMe" type="checkbox">
                            </#if>
                            <label for="rememberMe">
                                ${msg("rememberMe")}
                            </label>
                        </div>
                    </#if>
                    </div>
                </div>
                <div id="kc-form-buttons" class="field">
                <p class="control">
                    <input class="button is-primary is-fullwidth is-large" tabindex="4" name="login" id="kc-login" type="submit" value="${msg("doLogIn")}"/>
                </p>
            </form>
            <#if realm.resetPasswordAllowed>
                <div class="field">
                    <a class="level-item" href="${url.loginResetCredentialsUrl}">I forgot my password</a>
                </div>
            </#if>
            <#if realm.registrationAllowed && !registrationEmailAsUsername??&& !registrationDisabled??>
                <div class="field" style="margin-top: 2.5rem;">
                    <span>Don't have an account? <a href="${url.registrationUrl}"><strong>Create Your Account</strong></a></span>
                </div>
            </#if>
        </#if>
      </div>
    </div>
    <#elseif section = "socialProviders" >
    <div id="kc-form-social-providers">
        <div id="kc-form-wrapper">
            <#if realm.password && social?? && social.providers??>
            <div id="kc-social-providers">
                <hr/>
                <h2>${msg("identity-provider-login-label")}</h2>
                <ul>
                    <#list social.providers as p>
                        <div style="margin-top: 0.75rem">
                            <li>
                                <a id="social-${p.alias}" class="button is-outlined is-fullwidth is-normal identity-provider social-${p.alias}" type="button" href="${p.loginUrl}">
                                    <#if p.alias?has_content >
                                        <span class="icon is-small">
                                            <img src="${url.resourcesPath}/logos/${p.alias!}-logo.svg" alt="">
                                        </span>
                                        <span>${p.displayName!}</span>
                                        <span class="icon is-small"></span>
                                    <#else>
                                        <span>${p.displayName!}</span>
                                    </#if>
                                </a>
                            </li>
                        <div>
                    </#list>
                </ul>
            </div>
            </#if>
        </div>
    </div>
    </#if>

</@layout.registrationLayout>
