<#import "template.ftl" as layout>
<@layout.mainLayout active='totp' bodyClass='totp'; section>

<h2 class="title is-2">Mobile authenticator</h2>

    <#if totp.enabled>
        <p class="content">            
            You have currently set up a mobile authenticator for your account. You can unlink your account by pressing the button below.
        </p>
        <form action="${url.totpUrl}" method="post" class="form-inline">
            <input type="hidden" id="stateChecker" name="stateChecker" value="${stateChecker}">
            <input type="hidden" id="submitAction" name="submitAction" value="Delete">
            <div class="field">
                <button type="submit" id="remove-mobile" class="button is-danger">Disable</button>
            </div>
        </form>
    <#else>

    <p class="content">
        We recommend that you set up a mobile authenticator to improve your account security. With a mobile authenticator, every login to your account needs to be verified with a code from your phone. The steps below will guide you through the setup process.
    </p>
    <ol>
        <li>
            <p class="title is-6">${msg("totpStep1")}</p>

            <div class="columns">
                <div class="column">
                    <div class="card">
                        <div class="card-content has-text-centered">
                            <p class="title">
                                FreeOTP
                            </p>
                        </div>
                        <footer class="card-footer">
                            <p class="card-footer-item">
                            <span>
                                <a href="https://itunes.apple.com/us/app/freeotp-authenticator/id872559395"><span class="icon is-large"><i class="fab fa-app-store"></i></span></a>
                            </span>
                            </p>
                            <p class="card-footer-item">
                            <span>
                                <a href="https://play.google.com/store/apps/details?id=org.fedorahosted.freeotp"><span class="icon is-large"><i class="fab fa-google-play"></i></span></a>
                            </span>
                            </p>
                        </footer>
                    </div>
                </div>
                <div class="column">
                    <div class="card">
                        <div class="card-content has-text-centered">
                            <p class="title">
                                Google Authenticator
                            </p>
                            
                        </div>
                        <footer class="card-footer">
                            <p class="card-footer-item">
                            <span>
                                <a href="https://itunes.apple.com/us/app/google-authenticator/id388497605"><span class="icon is-large"><i class="fab fa-app-store"></i></span></a>
                            </span>
                            </p>
                            <p class="card-footer-item">
                            <span>
                                <a href="https://play.google.com/store/apps/details?id=com.google.android.apps.authenticator2"><span class="icon is-large"><i class="fab fa-google-play"></i></span></a>
                            </span>
                            </p>
                        </footer>
                    </div>
                </div>
            </div>
        </li>
    <#if mode?? && mode = "manual">
        <li>
            <p class="title is-6">${msg("totpManualStep2")}</p>
            <p><strong>${totp.totpSecretEncoded}</strong></p>
            <p class="has-text-link"><a href="${totp.qrUrl}" id="mode-barcode">${msg("totpScanBarcode")}</a></p>
        </li>
        <li>                        
            <p class="title is-6">${msg("totpManualStep3")}</p>
            <ul>
                <li id="kc-totp-type">${msg("totpType")}: ${msg("totp." + totp.policy.type)}</li>
                <li id="kc-totp-algorithm">${msg("totpAlgorithm")}: ${totp.policy.getAlgorithmKey()}</li>
                <li id="kc-totp-digits">${msg("totpDigits")}: ${totp.policy.digits}</li>
                <#if totp.policy.type = "totp">
                    <li id="kc-totp-period">${msg("totpInterval")}: ${totp.policy.period}</li>
                <#elseif totp.policy.type = "hotp">
                    <li id="kc-totp-counter">${msg("totpCounter")}: ${totp.policy.initialCounter}</li>
                </#if>
            </ul>
        </li>
    <#else>
        <li>
            <p class="title is-6">${msg("totpStep2")}</p>
            <p><img src="data:image/png;base64, ${totp.totpSecretQrCode}" alt="Figure: Barcode"></p>
            <p class="has-text-link"><a href="${totp.manualUrl}" id="mode-manual">${msg("totpUnableToScan")}</a></p>
        </li>
    </#if>
    <li>
        <p class="title is-6">${msg("totpStep3")}</p>
        <form action="${url.totpUrl}" method="post" novalidate>
            <input type="hidden" id="stateChecker" name="stateChecker" value="${stateChecker}">
            <div class="field">
                <label for="totp" class="label">${msg("authenticatorCode")}</label>
                <div class="control is-expanded">
                    <input type="text" pattern="\d*" class="input" id="totp" name="totp" autocomplete="off" autofocus autocomplete="off">
                    <input type="hidden" id="totpSecret" name="totpSecret" value="${totp.totpSecret}" />
                </div>
            </div>
            <div class="field">
                <button type="submit" class="button is-primary is-large is-fullwidth" name="submitAction" value="Save">${msg("doSave")}</button>
            </div>
        </form>
    </li>
</ol>

</#if>
</@layout.mainLayout>
