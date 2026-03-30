<#import "template.ftl" as layout>
<@layout.registrationLayout; section>
    <#if section = "header">
        ${msg("emailVerifyTitle")}
    <#elseif section = "form">
        <p class="instruction">
            ${msg("emailVerifyInstruction1")}
        </p>
        <hr class="hr">
        <p class="instruction">
            <a href="${url.loginAction}">${msg("emailVerifyInstruction2")} ${msg("doClickHere")} ${msg("emailVerifyInstruction3")}</a>
        </p>
    </#if>
</@layout.registrationLayout>