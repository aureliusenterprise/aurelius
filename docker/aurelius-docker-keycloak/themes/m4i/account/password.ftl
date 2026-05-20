<#import "template.ftl" as layout>
<@layout.mainLayout active='password' bodyClass='password'; section>

        <h2 class="title is-2">
            ${msg("changePasswordHtmlTitle")}
        </h2>
        <h5 class="subtitle is-5">
            ${msg("allFieldsRequired")}
        </h5>

    <form action="${url.passwordUrl}" class="form-horizontal" method="post">
        <input type="text" id="username" name="username" value="${(account.username!'')}" autocomplete="username" readonly="readonly" style="display:none;">

        <#if password.passwordSet>
            <div class="field">
                <label for="password" class="label">${msg("password")}</label>
                <div class="control is-expanded">
                    <input type="password" class="input" id="password" name="password" autofocus autocomplete="current-password">
                </div>
            </div>
        </#if>

        <input type="hidden" id="stateChecker" name="stateChecker" value="${stateChecker}">

        <div class="field">
            <label for="password-new" class="label">${msg("passwordNew")}</label>
            <div class="control is-expanded">
                <input type="password" class="input" id="password-new" name="password-new" autocomplete="new-password">
            </div>
        </div>

        <div class="field">
            <label for="password-confirm" class="label" class="two-lines">${msg("passwordConfirm")}</label>
            <div class="control is-expanded">
                <input type="password" class="input" id="password-confirm" name="password-confirm" autocomplete="new-password">
            </div>
        </div>

        <div class="field">
            <button type="submit" class="button is-primary" name="submitAction" value="Save">${msg("doSave")}</button>
        </div>
    </form>

</@layout.mainLayout>
