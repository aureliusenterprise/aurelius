<#import "template.ftl" as layout>
<@layout.mainLayout active='account' bodyClass='user'; section>

    <h2 class="title is-2">${msg("editAccountHtmlTitle")}</h2>
    <h5 class="subtitle is-5"><span class="required">*</span> ${msg("requiredFields")}</h5>

    <form action="${url.accountUrl}" method="post">

        <input type="hidden" id="stateChecker" name="stateChecker" value="${stateChecker}">
        <input type="hidden" class="input" id="username" name="username" disabled="disabled" value="${(account.username!'')}"/>
        <input type="hidden" class="input" id="email" name="email" value="${(account.email!'')}"/>

        <#if !realm.registrationEmailAsUsername>
            <div class="field">
                <label for="username" class="label">${msg("username")}</label>
                <div class="control is-expanded">
                    <input type="text" class="input" id="usernameDisplay" disabled="disabled" value="${(account.username!'')}"/>
                </div>
            </div>
        </#if>

        <div class="field">
            <label for="email" class="label">${msg("email")}</label>
            <div class="control">
                <input type="text" class="input" id="emailDisplay" disabled="disabled" value="${(account.email!'')}"/>
            </div>
        </div>

        <div class="field">
            <label for="firstName" class="label">${msg("firstName")}<span class="required"> *</span></label>
            <div class="control">
                <input type="text" class="input" id="firstName" name="firstName" value="${(account.firstName!'')}"/>
            </div>
        </div>

        <div class="field">
            <label for="lastName" class="label">${msg("lastName")}<span class="required"> *</span></label>
            <div class="control">
                <input type="text" class="input" id="lastName" name="lastName" value="${(account.lastName!'')}"/>
            </div>
        </div>

        <div class="field">
            <button type="submit" class="button is-primary" name="submitAction" value="Save">${msg("doSave")}</button>
            <button type="submit" class="button is-secondary" name="submitAction" value="Cancel">${msg("doCancel")}</button>
        </div>
    </form>

</@layout.mainLayout>