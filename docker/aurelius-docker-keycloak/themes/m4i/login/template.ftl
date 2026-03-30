<#macro registrationLayout bodyClass="" displayInfo=false displayMessage=true displayWide=false>
<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN"  "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">
<html xmlns="http://www.w3.org/1999/xhtml" class="${properties.kcHtmlClass!}">

<head>
    <meta charset="utf-8">
    <meta http-equiv="Content-Type" content="text/html; charset=UTF-8" />
    <meta name="robots" content="noindex, nofollow">

    <#if properties.meta?has_content>
        <#list properties.meta?split(' ') as meta>
            <meta name="${meta?split('==')[0]}" content="${meta?split('==')[1]}"/>
        </#list>
    </#if>
    <title>${msg("loginTitle",(realm.displayName!''))}</title>
    <link rel="icon" href="${url.resourcesPath}/img/favicon.ico" />
    <#if properties.styles?has_content>
        <#list properties.styles?split(' ') as style>
            <link href="${url.resourcesPath}/${style}" rel="stylesheet" />
        </#list>
    </#if>
    <#if properties.scripts?has_content>
        <#list properties.scripts?split(' ') as script>
            <script src="${url.resourcesPath}/${script}" type="text/javascript"></script>
        </#list>
    </#if>
    <#if scripts??>
        <#list scripts as script>
            <script src="${script}" type="text/javascript"></script>
        </#list>
    </#if>
    <!-- Load FontAwesome -->
    <script defer src="${url.resourcesPath}/js/solid.min.js"></script>
    <script defer src="${url.resourcesPath}/js/fontawesome.min.js"></script>
</head>

<body>
  <section class="hero is-light is-fullheight">
    <div class="hero-body">
        <div class="container has-text-centered">
            <div class="column is-4 is-offset-4">
                <img class="logo" src="${url.resourcesPath}/img/m4i-logo-notext.png" alt="Models4Insight" />
                <hr class="hr">
                <div class="box">
                    <h1 id="kc-page-title" class="title is-1"><#nested "header"></h1>
                    <hr class="hr">
                    <#if displayMessage && message?has_content>
                        <#if message.type = 'success'>
                            <article class="message is-success">
                                <div class="message-body">
                                    <span>${kcSanitize(message.summary)?no_esc}</span>
                                </div>
                            </article>
                        </#if>
                        <#if message.type = 'warning'>
                            <article class="message is-warning">
                                <div class="message-body">
                                    <span>${kcSanitize(message.summary)?no_esc}</span>
                                </div>
                            </article>
                        </#if>
                        <#if message.type = 'error'>
                            <article class="message is-danger">
                                <div class="message-body">
                                    <span>${kcSanitize(message.summary)?no_esc}</span>
                                </div>
                            </article>
                        </#if>
                        <#if message.type = 'info'>
                            <article class="message is-info">
                                <div class="message-body">
                                    <span>${kcSanitize(message.summary)?no_esc}</span>
                                </div>
                            </article>
                        </#if>
                    </#if>

                    <#nested "form">

                    <#if displayInfo>
                        <div id="kc-info">
                            <div id="kc-info-wrapper">
                                <#nested "info">
                            </div>
                        </div>
                    </#if>

                    <#nested "socialProviders">

                </div>
            </div>
        </div>
    </div>    
  </section>
</body>
</html>
</#macro>
