<#import "template.ftl" as layout>
<@layout.registrationLayout; section>
    <#if section = "header">
        ${msg("doLogIn")}
    <#elseif section = "form">
        <form id="kc-totp-login-form" action="${url.loginAction}" method="post" novalidate>
            <div class="field">
                <label for="totp" class="label">${msg("loginTotpOneTime")}</label>
                <div class="control has-icons-left is-expanded">
                    <input id="totp" pattern="\d*" name="totp" autocomplete="off" type="text" class="input" autofocus />
                    <span class="icon is-small is-left">
                        <i class="fas fa-key"></i>
                    </span>
                </div>
            </div>
            <hr class="hr">
            <div class="field">
                <input class="button is-primary is-large is-fullwidth" name="login" id="kc-login" type="submit" value="${msg("doLogIn")}"/>
            </div>
            <hr class="hr">
            <div class="content">
                A mobile authenticator is enabled for this account. Please check your authenticator app for a one-time login code.
            </div>
        </form>
    </#if>
</@layout.registrationLayout>