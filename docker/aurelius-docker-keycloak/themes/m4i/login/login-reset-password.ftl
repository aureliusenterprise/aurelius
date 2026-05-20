<#import "template.ftl" as layout>
<@layout.registrationLayout displayInfo=true; section>
    <#if section = "header">
        ${msg("emailForgotTitle")}
    <#elseif section = "form">
        <form id="kc-reset-password-form" action="${url.loginAction}" method="post">
            <div class="field">
                <label for="username" class="label"><#if !realm.loginWithEmailAllowed>${msg("username")}<#elseif !realm.registrationEmailAsUsername>${msg("usernameOrEmail")}<#else>${msg("email")}</#if></label>
                <div class="control has-icons-left is-expanded">
                    <input type="text" id="username" name="username" class="input" autofocus/>
                    <span class="icon is-small is-left">
                        <i class="fas fa-user"></i>
                    </span>
                </div>
            </div>
            <hr class="hr">
            <div id="kc-form-buttons" class="field">
                <input class="button is-primary is-large is-fullwidth" type="submit" value="${msg("doSubmit")}"/>
            </div>
            <div class="field">
                <span><a href="${url.loginUrl}">${kcSanitize(msg("backToLogin"))?no_esc}</a></span>
            </div>
        </form>
    <#elseif section = "info" >
        <hr class="hr">
        ${msg("emailInstruction")}
    </#if>
</@layout.registrationLayout>
