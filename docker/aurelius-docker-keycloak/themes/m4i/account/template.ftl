<#macro mainLayout active bodyClass>
<!doctype html>
<html>
<head>
    <meta charset="utf-8">
    <meta http-equiv="Content-Type" content="text/html; charset=UTF-8" />
    <meta name="robots" content="noindex, nofollow">

    <title>${msg("accountManagementTitle")}</title>
    <link rel="icon" href="${url.resourcesPath}/img/favicon.ico">
    <#if properties.styles?has_content>
        <#list properties.styles?split(' ') as style>
            <link href="${url.resourcesPath}/${style}" rel="stylesheet" />
        </#list>
    </#if>
    <#if properties.scripts?has_content>
        <#list properties.scripts?split(' ') as script>
            <script type="text/javascript" src="${url.resourcesPath}/${script}"></script>
        </#list>
    </#if>
    <!-- Load FontAwesome -->
    <script defer src="${url.resourcesPath}/js/solid.min.js"></script>
    <script defer src="${url.resourcesPath}/js/brands.min.js"></script>
    <script defer src="${url.resourcesPath}/js/fontawesome.min.js"></script>
</head>
<body class="has-background-light has-navbar-fixed-top" style="max-width: 100vw">

<nav class="navbar is-fixed-top has-background-light" role="navigation" aria-label="main navigation">
  <div class="container">
    <div class="navbar-brand">
      <a class="navbar-item is-size-4"><img src="${url.resourcesPath}/img/m4i-logo-notext.png" alt="Models4Insight" style="min-height: 50px;"/></a>
    </div>
    <div id="primaryNavMenu" class="navbar-menu">
      <div class="navbar-end">
        <#if referrer?has_content && referrer.url?has_content>
            <span class="navbar-item">
                <a class="button is-primary" href="${referrer.url}" id="referrer">${msg("backTo",referrer.name)}</a>
            </span>
        </#if>
        <span class="navbar-item">
            <a class="button is-secondary is-inverted" href="${url.logoutUrl}">${msg("doSignOut")}</a>
        </span>
        </div>
      </div>
    </div>
  </div>
</nav>
<section class="hero is-primary is-bold">
    <div class="hero-body">
        <div class="container has-text-centered">
            <h1 class="title is-1">Account Security</h1>
        </div>
    </div>
    <div class="hero-footer">
        <nav class="tabs is-boxed is-fullwidth">
            <div class="container">
                <ul>
                    <li class="<#if active=='account'>is-active</#if>"><a href="${url.accountUrl}">${msg("account")}</a></li>
                    <#if features.passwordUpdateSupported><li class="<#if active=='password'>is-active</#if>"><a href="${url.passwordUrl}">${msg("password")}</a></li></#if>
                    <li class="<#if active=='totp'>is-active</#if>"><a href="${url.totpUrl}">Mobile authenticator</a></li>
                </ul>
            </div>
        </nav>
    </div>
</section> 

<div class="container" style="min-height: 70vh;">  
    <#if message?has_content>
        <div class="section">
            <div class="alert alert-${message.type}">
                <#if message.type = 'success'>
                    <article class="message is-success">
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
            </div>
        </div>
    </#if>
    <div class="section">
        <#nested "content">
    </div> 
</div>

<footer class="footer has-background-link">
  <div class="container has-text-centered has-text-white">
    <p>Models4Insight Account Security</p>
    <p>${kcSanitize(msg(properties.version))?no_esc}</p>
  </div>
</footer>


</body>
</html>
</#macro>