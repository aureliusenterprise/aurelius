<#import "template.ftl" as layout>
<@layout.registrationLayout displayInfo=true; section>
    <#if section = "header">
        ${msg("updatePasswordTitle")}
    <#elseif section = "form">
        <form id="kc-passwd-update-form" class="${properties.kcFormClass!}" action="${url.loginAction}" method="post">

            <input type="text" class="input" id="username" name="username" value="${username}" autocomplete="username" readonly="readonly" style="display:none;"/>

            <input type="password" class="input" id="password" name="password" autocomplete="current-password" style="display:none;"/>

            <div class="field">
                <label for="password-new" class="label">${msg("passwordNew")}</label>
                <div class="control has-icons-left is-expanded">
                    <input type="password" id="password-new" name="password-new" class="input" autofocus autocomplete="new-password" />
                </div>
            </div>

            <div class="field">
                <label for="password-confirm" class="label">${msg("passwordConfirm")}</label>
                <div class="control has-icons-left is-expanded">
                    <input type="password" id="password-confirm" name="password-confirm" class="input" autocomplete="new-password" />
                </div>
            </div>

            <hr class="hr">
            
            <div class="field">
                <input class="button is-primary is-large is-fullwidth" type="submit" value="${msg("doSubmit")}"/>
            </div>
        </form>
    </#if>
</@layout.registrationLayout>
