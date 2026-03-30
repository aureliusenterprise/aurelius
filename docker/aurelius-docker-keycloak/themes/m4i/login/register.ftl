<#import "template.ftl" as layout>
<@layout.registrationLayout; section>
    <#if section = "title">
        ${msg("Create Your Account",(realm.displayName!''))}
    <#elseif section = "header">
        ${msg("Create Your Account",(realm.displayNameHtml!''))?no_esc}
    <#elseif section = "form">
        <form id="kc-register-form" action="${url.registrationAction}" method="post">
            <div class="field">
                <label class="label" for="firstName">First Name *</label>
                <div class="control is-expanded">
                    <input type="text" id="firstName" class="input" name="firstName" value="${(register.formData.firstName!'')}" />
                </div>
            </div>

            <div class="field">
                <label class="label" for="lastName">Last Name *</label>
                <div class="control is-expanded">
                    <input type="text" id="lastName" class="input" name="lastName" value="${(register.formData.lastName!'')}" />
                </div>
            </div>

            <div class="field">
                <label class="label" for="email">${msg("email")} *</label>
                <div class="control has-icons-left is-expanded">
                    <input type="text" id="email" class="input" name="email" value="${(register.formData.email!'')}" autocomplete="email" />
                    <span class="icon is-small is-left">
                        <i class="fas fa-envelope"></i>
                    </span>
                </div>
            </div>

          <#if !realm.registrationEmailAsUsername>
            <div class="field">
                <label class="label" for="username">${msg("username")} *</label>
                <div class="control has-icons-left is-expanded">
                    <input type="text" id="usernameR" class="input" name="username" value="${(register.formData.username!'')}" autocomplete="username" />
		<i>Usernames must be at least 3 characters long, using lower case and  must consist of a-z, _, and 0-9 characters.</i>
                    <span class="icon is-small is-left">
                        <i class="fas fa-user"></i>
                    </span>
                </div>
            </div>
          </#if>

            <#if passwordRequired>
            <div class="field">
                <label class="label" for="password">${msg("password")} *</label>
                <div class="control has-icons-left is-expanded">
                    <input type="password" id="password" class="input" name="password" autocomplete="new-password"/>
                    <span class="icon is-small is-left">
                        <i class="fas fa-key"></i>
                    </span>
                </div>
            </div>

            <div class="field">
                <label class="label" for="password-confirm">Confirm Password *</label>
                <div class="control has-icons-left is-expanded">
                    <input type="password" id="password-confirm" class="input" name="password-confirm" />
                    <span class="icon is-small is-left">
                        <i class="fas fa-key"></i>
                    </span>
                </div>
            </div>
            </#if>

            <div class="field">
                <label class="label" for="user.attributes.phoneNumber">Phone Number</label>
                <div class="control has-icons-left is-expanded">
                    <input type="tel" 
                           id="user.attributes.phoneNumber" 
                           class="input" 
                           name="user.attributes.phoneNumber" 
                           value="${(register.formData['user.attributes.phoneNumber']!'')}"
                           placeholder="e.g., +1 (555) 123-4567"
                           pattern="[\+\d\s\(\)-]{5,20}"
                           title="Phone number should contain only +, (), spaces, and numbers. Length: 5-20 characters." />
                    <span class="icon is-small is-left">
                        <i class="fas fa-phone"></i>
                    </span>
                </div>
            </div>

            <div class="field">
                <label class="label" for="user.attributes.countryRegion">Country</label>
                <div class="control has-icons-left is-expanded">
                    <input type="text" id="user.attributes.countryRegion" class="input" name="user.attributes.countryRegion" value="${(register.formData['user.attributes.countryRegion']!'')}" />
                    <span class="icon is-small is-left">
                        <i class="fas fa-globe"></i>
                    </span>
                </div>
            </div>

            <div class="field">
                <label class="label" for="user.attributes.areaOfInterest">Area of Interest</label>
                <div class="control has-icons-left is-expanded">
                    <input type="text" id="user.attributes.areaOfInterest" class="input" name="user.attributes.areaOfInterest" value="${(register.formData['user.attributes.areaOfInterest']!'')}" />
                    <span class="icon is-small is-left">
                        <i class="fas fa-lightbulb"></i>
                    </span>
                </div>
            </div>

            <div class="field">
                <label class="label" for="user.attributes.companyName">Company Name</label>
                <div class="control has-icons-left is-expanded">
                    <input type="text" id="user.attributes.companyName" class="input" name="user.attributes.companyName" value="${(register.formData['user.attributes.companyName']!'')}" />
                    <span class="icon is-small is-left">
                        <i class="fas fa-building"></i>
                    </span>
                </div>
            </div>

            <div class="field">
                <label class="label" for="user.attributes.positionRole">Position/Role</label>
                <div class="control has-icons-left is-expanded">
                    <input type="text" id="user.attributes.positionRole" class="input" name="user.attributes.positionRole" value="${(register.formData['user.attributes.positionRole']!'')}" />
                    <span class="icon is-small is-left">
                        <i class="fas fa-user-tie"></i>
                    </span>
                </div>
            </div>  

            <div class="field">
                <div class="control">
                    <#if register.formData['user.attributes.termsAgreement']?? && register.formData['user.attributes.termsAgreement'] == 'true'>
                        <input class="is-checkradio" id="user.attributes.termsAgreement" name="user.attributes.termsAgreement" type="checkbox" value="true" checked required>
                    <#else>
                        <input class="is-checkradio" id="user.attributes.termsAgreement" name="user.attributes.termsAgreement" type="checkbox" value="true" required>
                    </#if>
                    <label for="user.attributes.termsAgreement">
                        I agree to the <a id="myTerms"><i>Terms of Service</i></a> and the <a id="myPrivacy"><i>Privacy Policy</i></a> *
                    </label>
                </div>
            </div>

            <#if recaptchaRequired??>
                <div class="field">
                    <div class="g-recaptcha" data-size="compact" data-sitekey="${recaptchaSiteKey}"></div>
                </div>
            </#if>

            <hr class="hr">

            <div id="kc-form-buttons" class="field">
                <input id="regButton" class="button is-primary is-large is-fullwidth" type="submit" value="${msg("doRegister")}"/>
            </div>

            <div class="field">
                <span><a href="${url.loginUrl}">${msg("backToLogin")?no_esc}</a></span>
            </div>

            <hr class="hr">
        </form>

<!--  ===================== Terms of Service =================================================== -->
<div id="tosModal" class="modal">
  <div id="tosBackground" class="modal-background"></div>
  <div class="modal-card">
    <header class="modal-card-head">
      <p class="modal-card-title">Terms of Service</p>
      <button id="tosClose" class="delete" aria-label="close"></button>
    </header>
    <section class="modal-card-body">
      <h2 style='margin-top:0cm;margin-right:0cm;margin-bottom:3.0pt;margin-left:
0cm;line-height:16.0pt'><span style='font-size:10.0pt;font-family:"&amp;quot",serif;
color:#3D464D'>Models4Insight Terms of Service</span></h2>

<p style='margin-top:0cm;margin-right:0cm;margin-bottom:9.75pt;margin-left:
0cm;line-height:15.6pt'><span style='font-size:10.0pt;font-family:"&amp;quot",serif;
color:#3D464D'>Posted: January <span style='mso-spacerun:yes'> </span>02, 2018</span></p>

<p style='margin-top:0cm;margin-right:0cm;margin-bottom:9.75pt;margin-left:
0cm;line-height:15.6pt'><span style='font-size:10.0pt;font-family:"&amp;quot",serif;
color:#3D464D'>Effective: January 23, 2017</span></p>

<p style='margin-top:0cm;margin-right:0cm;margin-bottom:9.75pt;margin-left:
0cm;line-height:15.6pt'><span style='font-size:10.0pt;font-family:"&amp;quot",serif;
color:#3D464D'>Thanks for using Models4Insight These terms of service (&quot;<b>Terms</b>&quot;)
cover your use and access to our services, client software and websites (&quot;<b>Services</b>&quot;).
Your agreement is with Aurelius Enterprise Software B.V., the solely owner of
Models4Insight. Our </span><a href="http://www.models4insight.com/privacy"
target="_blank"><span style='font-size:10.0pt;font-family:"&amp;quot",serif;
color:#0070E0'>Privacy Policy</span></a><span style='font-size:10.0pt;
font-family:"&amp;quot",serif;color:#3D464D'> explains how we collect and use
your information while our </span><a
href="http://www.models4insight.com/terms#acceptable_use" target="_blank"><span
style='font-size:10.0pt;font-family:"&amp;quot",serif;color:#0070E0'>Acceptable
Use Policy</span></a><span style='font-size:10.0pt;font-family:"&amp;quot",serif;
color:#3D464D'> outlines your responsibilities when using our Services. By
using our Services, you're agreeing to be bound by these Terms, our </span><a
href="http://www.models4insight.com/privacy" target="_blank"><span
style='font-size:10.0pt;font-family:"&amp;quot",serif;color:#0070E0'>Privacy
Policy</span></a><span style='font-size:10.0pt;font-family:"&amp;quot",serif;
color:#3D464D'> and </span><a
href="https://www.models4insight.com/terms#acceptable_use" target="_blank"><span
style='font-size:10.0pt;font-family:"&amp;quot",serif;color:#0070E0'>Acceptable
Use Policy</span></a><span style='font-size:10.0pt;font-family:"&amp;quot",serif;
color:#3D464D'>. If you're using our Services for an organization, you're
agreeing to these Terms on behalf of that organization. </span></p>

<h2 style='margin-top:0cm;margin-right:0cm;margin-bottom:3.0pt;margin-left:
0cm;line-height:16.0pt'><span style='font-size:10.0pt;font-family:"&amp;quot",serif;
color:#3D464D'>Your Stuff &amp; Your Permissions</span></h2>

<p style='margin-top:0cm;margin-right:0cm;margin-bottom:9.75pt;margin-left:
0cm;line-height:15.6pt'><span style='font-size:10.0pt;font-family:"&amp;quot",serif;
color:#3D464D'>When you use our Services, you provide us with things like your
files, content, messages, contacts and so on (&quot;<b>Your Stuff</b>&quot;).
Your Stuff is yours. These Terms don't give us any rights to Your Stuff except
for the limited rights that enable us to offer the Services. </span></p>

<p style='margin-top:0cm;margin-right:0cm;margin-bottom:9.75pt;margin-left:
0cm;line-height:15.6pt'><span style='font-size:10.0pt;font-family:"&amp;quot",serif;
color:#3D464D'>You need to choose for the public or private domain option to be
able to use our Services. We need your permission to do things like hosting
Your Stuff, backing it up, and sharing it when you ask us to. Our Services also
provide you with features like store and retrieve, version control, conflict
analysis, branching , editing and sharing. These and other features may require
our systems to access, store and scan Your Stuff. You give us permission to do
those things, and this permission extends to our affiliates and trusted third
parties we work with.</span></p>

<p style='margin-top:0cm;margin-right:0cm;margin-bottom:9.75pt;margin-left:
0cm;line-height:15.6pt'><span style='font-size:10.0pt;font-family:"&amp;quot",serif;
color:#3D464D'>Additionally if you use the public domain of the service, you
automatically grant full permission to other parties to:</span></p>

<p style='margin-top:0cm;margin-right:0cm;margin-bottom:9.75pt;margin-left:
36.0pt;text-indent:-18.0pt;line-height:15.6pt;mso-list:l4 level1 lfo8'><![if !supportLists]><span
style='font-size:10.0pt;font-family:Symbol;mso-fareast-font-family:Symbol;
mso-bidi-font-family:Symbol;color:#3D464D'><span style='mso-list:Ignore'>·<span
style='font:7.0pt "Times New Roman"'>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;
</span></span></span><![endif]><span style='font-size:10.0pt;font-family:"&amp;quot",serif;
color:#3D464D'>See Your Stuff;</span></p>

<p style='margin-top:0cm;margin-right:0cm;margin-bottom:9.75pt;margin-left:
36.0pt;text-indent:-18.0pt;line-height:15.6pt;mso-list:l4 level1 lfo8'><![if !supportLists]><span
style='font-size:10.0pt;font-family:Symbol;mso-fareast-font-family:Symbol;
mso-bidi-font-family:Symbol;color:#3D464D'><span style='mso-list:Ignore'>·<span
style='font:7.0pt "Times New Roman"'>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;
</span></span></span><![endif]><span style='font-size:10.0pt;font-family:"&amp;quot",serif;
color:#3D464D'>Copy Your Stuff and rename it under another name as Their stuff;</span></p>

<p style='margin-top:0cm;margin-right:0cm;margin-bottom:9.75pt;margin-left:
36.0pt;text-indent:-18.0pt;line-height:15.6pt;mso-list:l4 level1 lfo8'><![if !supportLists]><span
style='font-size:10.0pt;font-family:Symbol;mso-fareast-font-family:Symbol;
mso-bidi-font-family:Symbol;color:#3D464D'><span style='mso-list:Ignore'>·<span
style='font:7.0pt "Times New Roman"'>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;
</span></span></span><![endif]><span style='font-size:10.0pt;font-family:"&amp;quot",serif;
color:#3D464D'>Modify Your stuff and store it under another name as Their
Stuff;</span></p>

<p style='margin-top:0cm;margin-right:0cm;margin-bottom:9.75pt;margin-left:
36.0pt;text-indent:-18.0pt;line-height:15.6pt;mso-list:l4 level1 lfo8'><![if !supportLists]><span
style='font-size:10.0pt;font-family:Symbol;mso-fareast-font-family:Symbol;
mso-bidi-font-family:Symbol;color:#3D464D'><span style='mso-list:Ignore'>·<span
style='font:7.0pt "Times New Roman"'>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;
</span></span></span><![endif]><span style='font-size:10.0pt;font-family:"&amp;quot",serif;
color:#3D464D'>Use your stuff after it is copy and store under another name as
Their Stuff;</span></p>

<h2 style='margin-top:0cm;margin-right:0cm;margin-bottom:3.0pt;margin-left:
0cm;line-height:16.0pt'><span style='font-size:10.0pt;font-family:"&amp;quot",serif;
color:#3D464D'>Sharing Your Stuff</span></h2>

<p style='margin-top:0cm;margin-right:0cm;margin-bottom:9.75pt;margin-left:
0cm;line-height:15.6pt'><span style='font-size:10.0pt;font-family:"&amp;quot",serif;
color:#3D464D'>Our Services let you share Your Stuff with others, so please
think carefully about what you share. </span></p>

<h2 style='margin-top:0cm;margin-right:0cm;margin-bottom:3.0pt;margin-left:
0cm;line-height:16.0pt'><span style='font-size:10.0pt;font-family:"&amp;quot",serif;
color:#3D464D'>Your Responsibilities</span></h2>

<p style='margin-top:0cm;margin-right:0cm;margin-bottom:9.75pt;margin-left:
0cm;line-height:15.6pt'><span style='font-size:10.0pt;font-family:"&amp;quot",serif;
color:#3D464D'>You're responsible for your conduct. Your Stuff and you must
comply with our </span><a href="http://www.models4insight.com/terms#acceptable_use"
target="_blank"><span style='font-size:10.0pt;font-family:"&amp;quot",serif;
color:#0070E0'>Acceptable Use Policy</span></a><span style='font-size:10.0pt;
font-family:"&amp;quot",serif;color:#3D464D'>. Content in the Services may be
protected by others' intellectual property rights. Please don't copy, upload,
download or share content unless you have the right to do so. </span></p>

<p style='margin-top:0cm;margin-right:0cm;margin-bottom:9.75pt;margin-left:
0cm;line-height:15.6pt'><span style='font-size:10.0pt;font-family:"&amp;quot",serif;
color:#3D464D'>We may review your conduct and content for compliance with these
Terms and our </span><a href="http://www.models4insight.com/terms#acceptable_use"
target="_blank"><span style='font-size:10.0pt;font-family:"&amp;quot",serif;
color:#0070E0'>Acceptable Use Policy</span></a><span style='font-size:10.0pt;
font-family:"&amp;quot",serif;color:#3D464D'>. With that said, we have no
obligation to do so. We aren't responsible for the content people post and
share via the Services. </span></p>

<p style='margin-top:0cm;margin-right:0cm;margin-bottom:9.75pt;margin-left:
0cm;line-height:15.6pt'><span style='font-size:10.0pt;font-family:"&amp;quot",serif;
color:#3D464D'>Help us keep you informed and Your Stuff protected. Safeguard your
password to the Services, and keep your account information current. Don't
share your account credentials or give others access to your account. </span></p>

<p style='margin-top:0cm;margin-right:0cm;margin-bottom:9.75pt;margin-left:
0cm;line-height:15.6pt'><span style='font-size:10.0pt;font-family:"&amp;quot",serif;
color:#3D464D'>You may use our Services only as permitted by applicable law,
including export control laws and regulations. </span></p>

<h2 style='margin-top:0cm;margin-right:0cm;margin-bottom:3.0pt;margin-left:
0cm;line-height:16.0pt'><span style='font-size:10.0pt;font-family:"&amp;quot",serif;
color:#3D464D'>Software</span></h2>

<p style='margin-top:0cm;margin-right:0cm;margin-bottom:9.75pt;margin-left:
0cm;line-height:15.6pt'><span style='font-size:10.0pt;font-family:"&amp;quot",serif;
color:#3D464D'>Some of our Services allow you to interact and integrate with
third party and/or open source software. At <span class=SpellE>anytime</span>
you are solely responsible to comply with the terms and conditions of these
parties. So long as you comply with these Terms, we give you the possibility to
interact and integrate with Our Services.<span style='mso-spacerun:yes'> 
</span>Unless the following restrictions are prohibited by law, you agree not
to reverse engineer or decompile the Services, attempt to do so, or assist
anyone in doing so. </span></p>

<h2 style='margin-top:0cm;margin-right:0cm;margin-bottom:3.0pt;margin-left:
0cm;line-height:16.0pt'><span style='font-size:10.0pt;font-family:"&amp;quot",serif;
color:#3D464D'>Beta Services</span></h2>

<p style='margin-top:0cm;margin-right:0cm;margin-bottom:9.75pt;margin-left:
0cm;line-height:15.6pt'><span style='font-size:10.0pt;font-family:"&amp;quot",serif;
color:#3D464D'>We sometimes release products and features that we are still
testing and evaluating. Those Services have been marked beta, preview, early
access, or evaluation (or with words or phrases with similar meanings) and may
not be as reliable as Aurelius Enterprise <span
style='mso-spacerun:yes'> </span>other services, so please keep that in mind. </span></p>

<h2 style='margin-top:0cm;margin-right:0cm;margin-bottom:3.0pt;margin-left:
0cm;line-height:16.0pt'><span style='font-size:10.0pt;font-family:"&amp;quot",serif;
color:#3D464D'>Our Stuff</span></h2>

<p style='margin-top:0cm;margin-right:0cm;margin-bottom:9.75pt;margin-left:
0cm;line-height:15.6pt'><span style='font-size:10.0pt;font-family:"&amp;quot",serif;
color:#3D464D'>The Services are protected by copyright, trademark, and other Dutch
and foreign laws. These Terms don't grant you any right, title or interest in
the Services, others' content in the Services, Models4Insight trademarks, logos
and other brand features. We welcome feedback, but note that we may use
comments or suggestions without any obligation to you. </span></p>

<h2 style='margin-top:0cm;margin-right:0cm;margin-bottom:3.0pt;margin-left:
0cm;line-height:16.0pt'><span style='font-size:10.0pt;font-family:"&amp;quot",serif;
color:#3D464D'>Copyright</span></h2>

<p style='margin-top:0cm;margin-right:0cm;margin-bottom:9.75pt;margin-left:
0cm;line-height:15.6pt'><span style='font-size:10.0pt;font-family:"&amp;quot",serif;
color:#3D464D'>We respect the intellectual property of others and ask that you
do too. We respond to notices of alleged copyright infringement if they comply
with the law, and such notices should be reported using our </span><span style='font-size:
10.0pt;font-family:"&amp;quot",serif;color:#0070E0'>Copyright Policy</span><span
style='font-size:10.0pt;font-family:"&amp;quot",serif;color:#3D464D'>. We
reserve the right to delete or disable content alleged to be infringing and
terminate accounts of repeat infringers. Our designated agent for notice of
alleged copyright infringement on the Services is: </span></p>

<p style='margin-top:0cm;margin-right:0cm;margin-bottom:9.75pt;margin-left:
0cm;line-height:15.6pt'><span style='font-size:10.0pt;font-family:"&amp;quot",serif;
color:#3D464D'>Copyright Agent<br>
Aurelius Enterprise Software B.V.<br>
Science Park 608 (Unit A10)<br>
1098 XH<span style='mso-spacerun:yes'>  </span>Amsterdam<br>
copyright@aureliusenterprise.com </span></p>

<h2 style='margin-top:0cm;margin-right:0cm;margin-bottom:3.0pt;margin-left:
0cm;line-height:16.0pt'><span style='font-size:10.0pt;font-family:"&amp;quot",serif;
color:#3D464D'>Paid Accounts</span></h2>

<p style='margin-top:0cm;margin-right:0cm;margin-bottom:9.75pt;margin-left:
0cm;line-height:15.6pt'><em><span style='font-size:10.0pt;font-family:"&amp;quot",serif;
color:#3D464D'>Billing</span></em><span style='font-size:10.0pt;font-family:
"&amp;quot",serif;color:#3D464D'>. You can increase your concept space and add
paid features to your account (turning your account into a &quot;<b>Paid
Account</b>&quot;). We'll automatically bill you from the date you convert to a
Paid Account and on each periodic renewal until cancellation. If you're on an
annual plan, we'll send you a notice email reminding you that your plan is
about to renew within a reasonable period of time prior to the renewal date.
You're responsible for all applicable taxes, and we'll charge tax when required
to do so. Some countries have mandatory local laws regarding your cancellation
rights, and this paragraph doesn't override these laws. </span></p>

<p style='margin-top:0cm;margin-right:0cm;margin-bottom:9.75pt;margin-left:
0cm;line-height:15.6pt'><em><span style='font-size:10.0pt;font-family:"&amp;quot",serif;
color:#3D464D'>No Refunds</span></em><span style='font-size:10.0pt;font-family:
"&amp;quot",serif;color:#3D464D'>. You may cancel your </span><span style='font-size:
10.0pt;font-family:"&amp;quot",serif;color:#0070E0'>Models4Insight Paid Account</span><span
style='font-size:10.0pt;font-family:"&amp;quot",serif;color:#3D464D'> at any
time. Refunds are only issued if </span><span
style='font-size:10.0pt;font-family:"&amp;quot",serif;color:#0070E0'>required
by law</span><span style='font-size:10.0pt;font-family:"&amp;quot",serif;
color:#3D464D'>. For example, users living in the European Union have the right
to cancel their Paid Account subscriptions within 14 days of signing up for,
upgrading to or renewing a Paid Account. </span></p>

<p style='margin-top:0cm;margin-right:0cm;margin-bottom:9.75pt;margin-left:
0cm;line-height:15.6pt'><em><span style='font-size:10.0pt;font-family:"&amp;quot",serif;
color:#3D464D'>Downgrades</span></em><span style='font-size:10.0pt;font-family:
"&amp;quot",serif;color:#3D464D'>. Your Paid Account will remain in effect
until it's cancelled or terminated under these Terms. If you don't pay for your
Paid Account on time, we reserve the right to suspend it or reduce your storage
to free space levels. </span></p>

<p style='margin-top:0cm;margin-right:0cm;margin-bottom:9.75pt;margin-left:
0cm;line-height:15.6pt'><em><span style='font-size:10.0pt;font-family:"&amp;quot",serif;
color:#3D464D'>Changes</span></em><span style='font-size:10.0pt;font-family:
"&amp;quot",serif;color:#3D464D'>. We may change the fees in effect but will
give you advance notice of these changes via a message to the email address
associated with your account. </span></p>

<h2 style='margin-top:0cm;margin-right:0cm;margin-bottom:3.0pt;margin-left:
0cm;line-height:16.0pt'><span style='font-size:10.0pt;font-family:"&amp;quot",serif;
color:#3D464D'>Models4Insight Corporate Account</span></h2>

<p style='margin-top:0cm;margin-right:0cm;margin-bottom:9.75pt;margin-left:
0cm;line-height:15.6pt'><em><span style='font-size:10.0pt;font-family:"&amp;quot",serif;
color:#3D464D'>Email address</span></em><span style='font-size:10.0pt;
font-family:"&amp;quot",serif;color:#3D464D'>. If you sign up for a Models4Insight
account with an email address provisioned by your organization, your
organization may be able to block your use of Models4Insight until you
transition to an account on a Models4Insight Corporate or you associate your Models4Insight
account with a personal email address. </span></p>

<p style='margin-top:0cm;margin-right:0cm;margin-bottom:9.75pt;margin-left:
0cm;line-height:15.6pt'><em><span style='font-size:10.0pt;font-family:"&amp;quot",serif;
color:#3D464D'>Using Models4Insight Corporate Account</span></em><span
style='font-size:10.0pt;font-family:"&amp;quot",serif;color:#3D464D'>. If you
join a Models4Insight Corporate account, you must use it in compliance with
your organization's terms and policies. Please note that Models4Insight
Corporate accounts are subject to your organization's control. Your
administrators may be able to access, disclose, restrict, or remove information
in or from your Modles4Insight Corporate account. They may also be able to
restrict or terminate your access to a Models4Insight Corporate account. If you
convert an existing Models4Insight account into part of a Models4Insight
Corporate account, your administrators may prevent you from later
disassociating your account from the Models4Insight Corporate account. </span></p>

<h2 style='margin-top:0cm;margin-right:0cm;margin-bottom:3.0pt;margin-left:
0cm;line-height:16.0pt'><span style='font-size:10.0pt;font-family:"&amp;quot",serif;
color:#3D464D'>Termination</span></h2>

<p style='margin-top:0cm;margin-right:0cm;margin-bottom:9.75pt;margin-left:
0cm;line-height:15.6pt'><span style='font-size:10.0pt;font-family:"&amp;quot",serif;
color:#3D464D'>You're free to stop using our Services at any time. We reserve
the right to suspend or terminate your access to the Services with notice to
you if: </span></p>

<p style='margin-top:0cm;margin-right:0cm;margin-bottom:9.75pt;margin-left:
30.0pt;line-height:15.6pt'><span style='font-size:10.0pt;font-family:"&amp;quot",serif;
color:#3D464D'>(a) you're in breach of these Terms, </span></p>

<p style='margin-top:0cm;margin-right:0cm;margin-bottom:9.75pt;margin-left:
30.0pt;line-height:15.6pt'><span style='font-size:10.0pt;font-family:"&amp;quot",serif;
color:#3D464D'>(b) you're using the Services in a manner that would cause a
real risk of harm or loss to us or other users, or </span></p>

<p style='margin-top:0cm;margin-right:0cm;margin-bottom:9.75pt;margin-left:
30.0pt;line-height:15.6pt'><span style='font-size:10.0pt;font-family:"&amp;quot",serif;
color:#3D464D'>(c) you don't have a Paid Account and haven't accessed our
Services for 6 consecutive months. </span></p>

<p style='margin-top:0cm;margin-right:0cm;margin-bottom:9.75pt;margin-left:
0cm;line-height:15.6pt'><span style='font-size:10.0pt;font-family:"&amp;quot",serif;
color:#3D464D'>We'll provide you with reasonable advance notice via the email
address associated with your account to remedy the activity that prompted us to
contact you and give you the opportunity to export Your Stuff from our
Services. If after such notice you fail to take the steps we ask of you, we'll
terminate or suspend your access to the Services. </span></p>

<p style='margin-top:0cm;margin-right:0cm;margin-bottom:9.75pt;margin-left:
0cm;line-height:15.6pt'><span style='font-size:10.0pt;font-family:"&amp;quot",serif;
color:#3D464D'>We won't provide notice before termination where: </span></p>

<p style='margin-top:0cm;margin-right:0cm;margin-bottom:9.75pt;margin-left:
30.0pt;line-height:15.6pt'><span style='font-size:10.0pt;font-family:"&amp;quot",serif;
color:#3D464D'>(a) you're in material breach of these Terms, </span></p>

<p style='margin-top:0cm;margin-right:0cm;margin-bottom:9.75pt;margin-left:
30.0pt;line-height:15.6pt'><span style='font-size:10.0pt;font-family:"&amp;quot",serif;
color:#3D464D'>(b) doing so would cause us legal liability or compromise our
ability to provide the Services to our other users, or </span></p>

<p style='margin-top:0cm;margin-right:0cm;margin-bottom:9.75pt;margin-left:
30.0pt;line-height:15.6pt'><span style='font-size:10.0pt;font-family:"&amp;quot",serif;
color:#3D464D'>(c) we're prohibited from doing so by law. </span></p>

<h2 style='margin-top:0cm;margin-right:0cm;margin-bottom:3.0pt;margin-left:
0cm;line-height:16.0pt'><span style='font-size:10.0pt;font-family:"&amp;quot",serif;
color:#3D464D'>Discontinuation of Services</span></h2>

<p style='margin-top:0cm;margin-right:0cm;margin-bottom:9.75pt;margin-left:
0cm;line-height:15.6pt'><span style='font-size:10.0pt;font-family:"&amp;quot",serif;
color:#3D464D'>We may decide to discontinue the Services in response to
unforeseen circumstances beyond Models4Insight, Aurelius Enterprise Software
B.V., control or to comply with a legal requirement. If we do so, we'll give
you reasonable prior notice so that you can export Your Stuff from our systems.
If we discontinue Services in this way before the end of any fixed or minimum
term you have paid us for, we'll refund the portion of the fees you have
pre-paid but haven't received Services for. </span></p>

<h2 style='margin-top:0cm;margin-right:0cm;margin-bottom:3.0pt;margin-left:
0cm;line-height:16.0pt'><span style='font-size:10.0pt;font-family:"&amp;quot",serif;
color:#3D464D'>Services &quot;AS IS&quot;</span></h2>

<p style='margin-top:0cm;margin-right:0cm;margin-bottom:9.75pt;margin-left:
0cm;line-height:15.6pt'><span style='font-size:10.0pt;font-family:"&amp;quot",serif;
color:#3D464D'>We strive to provide great Services, but there are certain
things that we can't guarantee. TO THE FULLEST EXTENT PERMITTED BY LAW, Models4Insight,
AURELIUS ENTERPRISE SOFTWARE B.V. AND ITS AFFILIATES, SUPPLIERS AND
DISTRIBUTORS MAKE NO WARRANTIES, EITHER EXPRESS OR IMPLIED, ABOUT THE SERVICES.
THE SERVICES ARE PROVIDED &quot;AS IS.&quot; WE ALSO DISCLAIM ANY WARRANTIES OF
MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NON-INFRINGEMENT. Some
places don't allow the disclaimers in this paragraph, so they may not apply to
you. </span></p>

<h2 style='margin-top:0cm;margin-right:0cm;margin-bottom:3.0pt;margin-left:
0cm;line-height:16.0pt'><span style='font-size:10.0pt;font-family:"&amp;quot",serif;
color:#3D464D'>Limitation of Liability</span></h2>

<p style='margin-top:0cm;margin-right:0cm;margin-bottom:9.75pt;margin-left:
0cm;line-height:15.6pt'><span style='font-size:10.0pt;font-family:"&amp;quot",serif;
color:#3D464D'>WE DON'T EXCLUDE OR LIMIT OUR LIABILITY TO YOU WHERE IT WOULD BE
ILLEGAL TO DO SO—THIS INCLUDES ANY LIABILITY FOR Models4Insight, AURELIUS
ENTERPRISE SOFTWARE B.V. OR ITS AFFILIATES' FRAUD OR FRAUDULENT
MISREPRESENTATION IN PROVIDING THE SERVICES. IN COUNTRIES WHERE THE FOLLOWING
TYPES OF EXCLUSIONS AREN'T ALLOWED, WE'RE RESPONSIBLE TO YOU ONLY FOR LOSSES
AND DAMAGES THAT ARE A REASONABLY FORESEEABLE RESULT OF OUR FAILURE TO USE
REASONABLE CARE AND SKILL OR OUR BREACH OF OUR CONTRACT WITH YOU. THIS
PARAGRAPH DOESN'T AFFECT CONSUMER RIGHTS THAT CAN'T BE WAIVED OR LIMITED BY ANY
CONTRACT OR AGREEMENT. </span></p>

<p style='margin-top:0cm;margin-right:0cm;margin-bottom:9.75pt;margin-left:
0cm;line-height:15.6pt'><span style='font-size:10.0pt;font-family:"&amp;quot",serif;
color:#3D464D'>IN COUNTRIES WHERE EXCLUSIONS OR LIMITATIONS OF LIABILITY ARE
ALLOWED, Models4Insght, AURELIUS ENTERPRISE SOFTWARE B.V., ITS AFFILIATES,
SUPPLIERS OR DISTRIBUTORS WON'T BE LIABLE FOR: </span></p>

<p style='margin-top:0cm;margin-right:0cm;margin-bottom:9.75pt;margin-left:
30.0pt;line-height:15.6pt'><span class=SpellE><span style='font-size:10.0pt;
font-family:"&amp;quot",serif;color:#3D464D'>i</span></span><span
style='font-size:10.0pt;font-family:"&amp;quot",serif;color:#3D464D'>. ANY INDIRECT,
SPECIAL, INCIDENTAL, PUNITIVE, EXEMPLARY OR CONSEQUENTIAL DAMAGES, OR </span></p>

<p style='margin-top:0cm;margin-right:0cm;margin-bottom:9.75pt;margin-left:
30.0pt;line-height:15.6pt'><span style='font-size:10.0pt;font-family:"&amp;quot",serif;
color:#3D464D'>ii. ANY LOSS OF USE, DATA, BUSINESS, OR PROFITS, REGARDLESS OF
LEGAL THEORY. </span></p>

<p style='margin-top:0cm;margin-right:0cm;margin-bottom:9.75pt;margin-left:
0cm;line-height:15.6pt'><span style='font-size:10.0pt;font-family:"&amp;quot",serif;
color:#3D464D'>THESE EXCLUSIONS OR LIMITATIONS WILL APPLY REGARDLESS OF WHETHER
OR NOT MODELS4INSIGHT OR ANY OF ITS AFFILIATES HAS BEEN WARNED OF THE
POSSIBILITY OF SUCH DAMAGES. </span></p>

<p style='margin-top:0cm;margin-right:0cm;margin-bottom:9.75pt;margin-left:
0cm;line-height:15.6pt'><span style='font-size:10.0pt;font-family:"&amp;quot",serif;
color:#3D464D'>IF YOU USE THE SERVICES FOR ANY COMMERCIAL, BUSINESS OR RE-SALE
PURPOSE, Models4Insight, AURELIUS ENTERPRISE SOFTWARE B.V., ITS AFFILIATES,
SUPPLIERS OR DISTRIBUTORS WILL HAVE NO LIABILITY TO YOU FOR ANY LOSS OF PROFIT,
LOSS OF BUSINESS, BUSINESS INTERRUPTION, OR LOSS OF BUSINESS OPPORTUNITY. MODELS4INSIGHT
AND ITS AFFILIATES AREN'T RESPONSIBLE FOR THE CONDUCT, WHETHER ONLINE OR
OFFLINE, OF ANY USER OF THE SERVICES. </span></p>

<p style='margin-top:0cm;margin-right:0cm;margin-bottom:9.75pt;margin-left:
0cm;line-height:15.6pt'><span style='font-size:10.0pt;font-family:"&amp;quot",serif;
color:#3D464D'>OTHER THAN FOR THE TYPES OF LIABILITY WE CANNOT LIMIT BY LAW (AS
DESCRIBED IN THIS SECTION), WE LIMIT OUR LIABILITY TO YOU TO THE GREATER OF </span><span
style='font-size:10.0pt;font-family:"Cambria",serif;color:#3D464D'>€</span><span
style='font-size:10.0pt;font-family:"&amp;quot",serif;color:#3D464D'>20 EURO OR
100% OF ANY AMOUNT YOU'VE PAID UNDER YOUR CURRENT SERVICE PLAN WITH MODELS4INSIGHT.
</span></p>

<h2 style='margin-top:0cm;margin-right:0cm;margin-bottom:3.0pt;margin-left:
0cm;line-height:16.0pt'><span style='font-size:10.0pt;font-family:"&amp;quot",serif;
color:#3D464D'>Resolving Disputes</span></h2>

<p style='margin-top:0cm;margin-right:0cm;margin-bottom:9.75pt;margin-left:
0cm;line-height:15.6pt'><em><span style='font-size:10.0pt;font-family:"&amp;quot",serif;
color:#3D464D'>Let's Try To Sort Things Out First</span></em><span
style='font-size:10.0pt;font-family:"&amp;quot",serif;color:#3D464D'>. We want
to address your concerns without needing a formal legal case. Before filing a
claim against Models4Insight, you agree to try to resolve the dispute
informally by contacting dispute-notice@models4insight.com. We'll try to
resolve the dispute informally by contacting you via email. If a dispute is not
resolved within 15 days of submission, you or Models4Insight may bring a formal
proceeding. </span></p>

<p style='margin-top:0cm;margin-right:0cm;margin-bottom:9.75pt;margin-left:
0cm;line-height:15.6pt'><em><span style='font-size:10.0pt;font-family:"&amp;quot",serif;
color:#3D464D'>Judicial forum for disputes</span></em><span style='font-size:
10.0pt;font-family:"&amp;quot",serif;color:#3D464D'>. You and Models4Insight,
agree that any judicial proceeding to resolve claims relating to these Terms or
the Services will be brought in the courts of Amsterdam, The Netherlands,
subject to the mandatory arbitration provisions below. Both you and Models4Insight
consent to venue and personal jurisdiction in such courts. If you reside in a
country (with laws that give consumers the right to bring disputes in their
local courts, this paragraph doesn't affect those requirements. </span></p>

<h2 style='margin-top:0cm;margin-right:0cm;margin-bottom:3.0pt;margin-left:
0cm;line-height:16.0pt'><span style='font-size:10.0pt;font-family:"&amp;quot",serif;
color:#3D464D'>Controlling Law</span></h2>

<p style='margin-top:0cm;margin-right:0cm;margin-bottom:9.75pt;margin-left:
0cm;line-height:15.6pt'><span style='font-size:10.0pt;font-family:"&amp;quot",serif;
color:#3D464D'>These Terms will be governed by Dutch law except for its
conflicts of laws principles. However, some countries have laws that require
agreements to be governed by the local laws of the consumer's country. This
paragraph doesn't override those laws. </span></p>

<h2 style='margin-top:0cm;margin-right:0cm;margin-bottom:3.0pt;margin-left:
0cm;line-height:16.0pt'><span style='font-size:10.0pt;font-family:"&amp;quot",serif;
color:#3D464D'>Entire Agreement</span></h2>

<p style='margin-top:0cm;margin-right:0cm;margin-bottom:9.75pt;margin-left:
0cm;line-height:15.6pt'><span style='font-size:10.0pt;font-family:"&amp;quot",serif;
color:#3D464D'>These Terms constitute the entire agreement between you and Models4Insight
with respect to the subject matter of these Terms, and supersede and replace
any other prior or contemporaneous agreements, or terms and conditions
applicable to the subject matter of these Terms. These Terms create no third
party beneficiary rights. </span></p>

<h2 style='margin-top:0cm;margin-right:0cm;margin-bottom:3.0pt;margin-left:
0cm;line-height:16.0pt'><span style='font-size:10.0pt;font-family:"&amp;quot",serif;
color:#3D464D'>Waiver, Severability &amp; Assignment</span></h2>

<p style='margin-top:0cm;margin-right:0cm;margin-bottom:9.75pt;margin-left:
0cm;line-height:15.6pt'><span style='font-size:10.0pt;font-family:"&amp;quot",serif;
color:#3D464D'>Models4Insight's failure to enforce a provision is not a waiver
of its right to do so later. If a provision is found unenforceable, the
remaining provisions of the Terms will remain in full effect and an enforceable
term will be substituted reflecting our intent as closely as possible. You may
not assign any of your rights under these Terms, and any such attempt will be
void. Models4Insight may assign its rights to any of its affiliates or subsidiaries,
or to any successor in interest of any business associated with the Services. </span></p>

<h2 style='margin-top:0cm;margin-right:0cm;margin-bottom:3.0pt;margin-left:
0cm;line-height:16.0pt'><span style='font-size:10.0pt;font-family:"&amp;quot",serif;
color:#3D464D'>Modifications</span></h2>

<p style='margin-top:0cm;margin-right:0cm;margin-bottom:9.75pt;margin-left:
0cm;line-height:15.6pt'><span style='font-size:10.0pt;font-family:"&amp;quot",serif;
color:#3D464D'>We may revise these Terms from time to time to better reflect: </span></p>

<p style='margin-top:0cm;margin-right:0cm;margin-bottom:9.75pt;margin-left:
30.0pt;line-height:15.6pt'><span style='font-size:10.0pt;font-family:"&amp;quot",serif;
color:#3D464D'>(a) changes to the law, </span></p>

<p style='margin-top:0cm;margin-right:0cm;margin-bottom:9.75pt;margin-left:
30.0pt;line-height:15.6pt'><span style='font-size:10.0pt;font-family:"&amp;quot",serif;
color:#3D464D'>(b) new regulatory requirements, or </span></p>

<p style='margin-top:0cm;margin-right:0cm;margin-bottom:9.75pt;margin-left:
30.0pt;line-height:15.6pt'><span style='font-size:10.0pt;font-family:"&amp;quot",serif;
color:#3D464D'>(c) improvements or enhancements made to our Services. </span></p>

<p style='margin-top:0cm;margin-right:0cm;margin-bottom:9.75pt;margin-left:
0cm;line-height:15.6pt'><span style='font-size:10.0pt;font-family:"&amp;quot",serif;
color:#3D464D'>If an update affects your use of the Services or your legal
rights as a user of our Services, we'll notify you prior to the update's
effective date by sending an email to the email address associated with your
account or via an in-product notification. These updated terms will be
effective no less than 30 days from when we notify you. </span></p>

<p style='margin-top:0cm;margin-right:0cm;margin-bottom:9.75pt;margin-left:
0cm;line-height:15.6pt'><span style='font-size:10.0pt;font-family:"&amp;quot",serif;
color:#3D464D'>If you don't agree to the updates we make, please cancel your
account before they become effective. Where applicable, we'll offer you a
prorated refund based on the amounts you have prepaid for Services and your
account cancellation date. By continuing to use or access the Services after
the updates come into effect, you agree to be bound by the revised Terms. </span></p>

<p class=MsoNormal></p>
    </section>
    <footer class="modal-card-foot">
      <button id="tosGotIt" class="button is-success">I got it</button>
    </footer>
  </div>
</div>
<!--  ===================== Privacy Policy =================================================== -->
<div id="privacyModal" class="modal">
    <div id="privacyBackground" class="modal-background"></div>
        <div class="modal-card">
            <header class="modal-card-head">
                <p class="modal-card-title">Privacy Policy</p>
                <button id="privacyClose" class="delete" aria-label="close"></button>
            </header>
            <section class="modal-card-body">

<h2 style='margin-top:0cm;margin-right:0cm;margin-bottom:3.0pt;margin-left:
0cm;line-height:16.0pt'><span style='font-size:10.0pt;font-family:"&amp;quot",serif;
color:#3D464D'>Models4Insight Privacy Policy</span></h2>

<p style='margin-top:0cm;margin-right:0cm;margin-bottom:9.75pt;margin-left:
0cm;line-height:15.6pt'><span style='font-size:10.0pt;font-family:"&amp;quot",serif;
color:#3D464D'>Posted: January 02, 2018</span></p>

<p style='margin-top:0cm;margin-right:0cm;margin-bottom:9.75pt;margin-left:
0cm;line-height:15.6pt'><span style='font-size:10.0pt;font-family:"&amp;quot",serif;
color:#3D464D'>Effective: January 23, 2018</span></p>

<p style='margin-top:0cm;margin-right:0cm;margin-bottom:9.75pt;margin-left:
0cm;line-height:15.6pt'><span style='font-size:10.0pt;font-family:"&amp;quot",serif;
color:#3D464D'>Thanks for using Models4Insight! Here we describe how we
collect, use and handle your information when you use our websites, software
and services (&quot;<b>Services</b>&quot;). </span></p>

<h2 style='margin-top:0cm;margin-right:0cm;margin-bottom:3.0pt;margin-left:
0cm;line-height:16.0pt'><span style='font-size:10.0pt;font-family:"&amp;quot",serif;
color:#3D464D'>What &amp; Why</span></h2>

<p style='margin-top:0cm;margin-right:0cm;margin-bottom:9.75pt;margin-left:
0cm;line-height:15.6pt'><span style='font-size:10.0pt;font-family:"&amp;quot",serif;
color:#3D464D'>We collect and use the following information to provide, improve
and protect our Services: </span></p>

<p style='margin-top:0cm;margin-right:0cm;margin-bottom:9.75pt;margin-left:
0cm;line-height:15.6pt'><em><span style='font-size:10.0pt;font-family:"&amp;quot",serif;
color:#3D464D'>Account</span></em><span style='font-size:10.0pt;font-family:
"&amp;quot",serif;color:#3D464D'>. We collect, and associate with your account,
information like your name, email address, phone number, payment info, physical
address, and account activity. Some of our services let you access your
accounts and your information with other service providers. </span></p>

<p style='margin-top:0cm;margin-right:0cm;margin-bottom:9.75pt;margin-left:
0cm;line-height:15.6pt'><em><span style='font-size:10.0pt;font-family:"&amp;quot",serif;
color:#3D464D'>Services</span></em><span style='font-size:10.0pt;font-family:
"&amp;quot",serif;color:#3D464D'>. Our Services are designed to make it simple
for you to store Your Stuff, collaborate with others, and work across multiple
devices. To make that possible, we store, process, and transmit Your Stuff—like
files, messages, comments, and models—as well as information related to it.
This related information can be things like your </span><a
href="http://www.models4insight.com/help/63" target="_blank"><span style='font-size:
10.0pt;font-family:"&amp;quot",serif;color:#0070E0;text-decoration:none;
text-underline:none'>profile information</span></a><span style='font-size:10.0pt;
font-family:"&amp;quot",serif;color:#3D464D'> that makes it easier to
collaborate and share Your Stuff with others. Our Services provide you with
different options for sharing Your Stuff. </span></p>

<p style='margin-top:0cm;margin-right:0cm;margin-bottom:9.75pt;margin-left:
0cm;line-height:15.6pt'><span style='font-size:10.0pt;font-family:"&amp;quot",serif;
color:#3D464D'>You may choose to give us access to your contacts to make it
easy for you to do things like share and collaborate on Your Stuff, send
messages, and invite others to use your models and the Services. If you do,
we'll store those contacts on our servers for you to use. </span></p>

<p style='margin-top:0cm;margin-right:0cm;margin-bottom:9.75pt;margin-left:
0cm;line-height:15.6pt'><em><span style='font-size:10.0pt;font-family:"&amp;quot",serif;
color:#3D464D'>Usage</span></em><span style='font-size:10.0pt;font-family:"&amp;quot",serif;
color:#3D464D'>. We collect information related to how you use the Services,
including actions you take in your account (like creating, branching, sharing,
editing, viewing, and moving models, files or folders). This helps us provide
you with better and new features. </span></p>

<p style='margin-top:0cm;margin-right:0cm;margin-bottom:9.75pt;margin-left:
0cm;line-height:15.6pt'><span style='font-size:10.0pt;font-family:"&amp;quot",serif;
color:#3D464D'>We also collect information from and about the devices you use
to access the Services. This includes things like IP addresses, the type of
browser and device you use, the web page you visited before coming to our
sites, and identifiers associated with your devices. Your devices (depending on
their settings) may also transmit location information to the Services. </span></p>

<p style='margin-top:0cm;margin-right:0cm;margin-bottom:9.75pt;margin-left:
0cm;line-height:15.6pt'><em><span style='font-size:10.0pt;font-family:"&amp;quot",serif;
color:#3D464D'>Cookies and other technologies</span></em><span
style='font-size:10.0pt;font-family:"&amp;quot",serif;color:#3D464D'>. We use
technologies like </span><a href="http://www.models4insight.com/terms/cookies"
target="_blank"><span style='font-size:10.0pt;font-family:"&amp;quot",serif;
color:#0070E0;text-decoration:none;text-underline:none'>cookies and pixel tags</span></a><span
style='font-size:10.0pt;font-family:"&amp;quot",serif;color:#3D464D'> to
provide, improve, protect and promote our Services. For example, cookies help
us with things like remembering your username for your next visit,
understanding how you are interacting with our Services, and improving them
based on that information. You can set your browser to not accept cookies, but
this may limit your ability to use the Services. If our systems receive a DNT:1
signal from your browser, we'll respond to that signal as outlined </span><a
href="http://www.models4insight.com/terms/cookies" target="_blank"><span
style='font-size:10.0pt;font-family:"&amp;quot",serif;color:#0070E0;text-decoration:
none;text-underline:none'>here</span></a><span style='font-size:10.0pt;
font-family:"&amp;quot",serif;color:#3D464D'>. </span></p>

<h2 style='margin-top:0cm;margin-right:0cm;margin-bottom:3.0pt;margin-left:
0cm;line-height:16.0pt'><span style='font-size:10.0pt;font-family:"&amp;quot",serif;
color:#3D464D'>With whom</span></h2>

<p style='margin-top:0cm;margin-right:0cm;margin-bottom:9.75pt;margin-left:
0cm;line-height:15.6pt'><span style='font-size:10.0pt;font-family:"&amp;quot",serif;
color:#3D464D'>We may share information as discussed below, but we won't sell
it to advertisers or other third parties. </span></p>

<p style='margin-top:0cm;margin-right:0cm;margin-bottom:9.75pt;margin-left:
0cm;line-height:15.6pt'><em><span style='font-size:10.0pt;font-family:"&amp;quot",serif;
color:#3D464D'>Others working for Models4Insight, Aurelius Enterprise Software <span
class=GramE>B.V.<span style='font-style:normal'>.</span></span></span></em><span
style='font-size:10.0pt;font-family:"&amp;quot",serif;color:#3D464D'>
Models4Insight, Aurelius Enterprise Software B.V. uses certain trusted third
parties (for example, providers of customer support and IT services) to help us
provide, improve, protect, and promote our Services. These third parties will
access your information only to perform tasks on our behalf in compliance with
this Privacy Policy, and we'll remain responsible for their handling of your
information per our instructions. </span></p>

<p style='margin-top:0cm;margin-right:0cm;margin-bottom:9.75pt;margin-left:
0cm;line-height:15.6pt'><em><span style='font-size:10.0pt;font-family:"&amp;quot",serif;
color:#3D464D'>Other users</span></em><span style='font-size:10.0pt;font-family:
"&amp;quot",serif;color:#3D464D'>. Our Services display information like your
name, profile picture, and email address to other users in places like your
user profile and sharing notifications. When you register your Models4Insight
account with an email address on a domain owned by your employer or
organization, we may help collaborators find you and your team by making some
of your basic information—like your name, team name, profile picture, and email
address—visible to other users on the same domain. This helps us show you teams
you can join, and helps other users share files and folders with you. </span></p>

<p style='margin-top:0cm;margin-right:0cm;margin-bottom:9.75pt;margin-left:
0cm;line-height:15.6pt'><span style='font-size:10.0pt;font-family:"&amp;quot",serif;
color:#3D464D'>Certain features let you make additional information available
to others. </span></p>

<p style='margin-top:0cm;margin-right:0cm;margin-bottom:9.75pt;margin-left:
0cm;line-height:15.6pt'><em><span style='font-size:10.0pt;font-family:"&amp;quot",serif;
color:#3D464D'>Other applications</span></em><span style='font-size:10.0pt;
font-family:"&amp;quot",serif;color:#3D464D'>. You can also give third parties
access to your information and account. Just remember that their use of your
information could be governed by their privacy policies and terms. </span></p>

<p style='margin-top:0cm;margin-right:0cm;margin-bottom:9.75pt;margin-left:
0cm;line-height:15.6pt'><em><span style='font-size:10.0pt;font-family:"&amp;quot",serif;
color:#3D464D'>Models4Insight Corporate Account Admins.</span></em><span
style='font-size:10.0pt;font-family:"&amp;quot",serif;color:#3D464D'> If you
are a user of a Models4Insight Corporate account your administrator may have the
ability to access and control your Models4Insight Corporate account. Please
refer to your organization's internal policies if you have questions about
this. If you are not a Models4Insight Corporate account user but interact with
a Models4Insight Corporate account user (by, for example, joining a shared
folder or accessing stuff shared by that user), members of that organization
may be able to view the name, email address, profile picture, and IP address
that was associated with your account at the time of that interaction. </span></p>

<p style='margin-top:0cm;margin-right:0cm;margin-bottom:9.75pt;margin-left:
0cm;line-height:15.6pt'><em><span style='font-size:10.0pt;font-family:"&amp;quot",serif;
color:#3D464D'>Law &amp; Order</span></em><span style='font-size:10.0pt;
font-family:"&amp;quot",serif;color:#3D464D'>. We may disclose your information
to third parties if we determine that such disclosure is reasonably necessary
to (a) comply with the law; (b) protect any person from death or serious bodily
injury; (c) prevent fraud or abuse of Models4Insight or our users; or (d)
protect Models4Insight's property rights. </span></p>

<p style='margin-top:0cm;margin-right:0cm;margin-bottom:9.75pt;margin-left:
0cm;line-height:15.6pt'><span style='font-size:10.0pt;font-family:"&amp;quot",serif;
color:#3D464D'>Stewardship of your data is critical to us and a responsibility
that we embrace. We believe that our users' data should receive the same legal
protections regardless of whether it's stored on our services or on their own
computer's hard drive. We'll abide by the following </span><a
href="http://www.models4insight.com/transparency" target="_blank"><span
style='font-size:10.0pt;font-family:"&amp;quot",serif;color:#0070E0;text-decoration:
none;text-underline:none'>Government Request Principles</span></a><span
style='font-size:10.0pt;font-family:"&amp;quot",serif;color:#3D464D'> when
receiving, scrutinizing and responding to government requests (including
national security requests) for our users' data: </span></p>

<ul type=disc>
 <li class=MsoNormal style='color:#3D464D;mso-margin-top-alt:auto;mso-margin-bottom-alt:
     auto;mso-list:l6 level1 lfo9;tab-stops:list 36.0pt'><span
     style='font-size:10.0pt;font-family:"&amp;quot",serif'>Be transparent,</span></li>
 <li class=MsoNormal style='color:#3D464D;mso-margin-top-alt:auto;mso-margin-bottom-alt:
     auto;mso-list:l6 level1 lfo9;tab-stops:list 36.0pt'><span
     style='font-size:10.0pt;font-family:"&amp;quot",serif'>Fight blanket
     requests,</span></li>
 <li class=MsoNormal style='color:#3D464D;mso-margin-top-alt:auto;mso-margin-bottom-alt:
     auto;mso-list:l6 level1 lfo9;tab-stops:list 36.0pt'><span
     style='font-size:10.0pt;font-family:"&amp;quot",serif'>Protect all users
     and</span></li>
 <li class=MsoNormal style='color:#3D464D;mso-margin-top-alt:auto;mso-margin-bottom-alt:
     auto;mso-list:l6 level1 lfo9;tab-stops:list 36.0pt'><span
     style='font-size:10.0pt;font-family:"&amp;quot",serif'>Provide trusted
     services.</span></li>
</ul>

<p class=MsoNormal><span style='font-size:10.0pt;font-family:"Arial",sans-serif;
color:#3D464D'>We publish a </span><a
href="http://www.models4insight.com/transparency/reports" target="_blank"><span
style='font-size:10.0pt;font-family:"&amp;quot",serif;color:#0070E0;text-decoration:
none;text-underline:none'>Transparency Report</span></a><span style='font-size:
10.0pt;font-family:"Arial",sans-serif;color:#3D464D'> as part of our commitment
to informing users about when and how governments ask us for information. This
report details the types and numbers of requests we receive from law
enforcement. We encourage users to review our </span><a
href="http://www.models4insight.com/transparency" target="_blank"><span
style='font-size:10.0pt;font-family:"&amp;quot",serif;color:#0070E0;text-decoration:
none;text-underline:none'>Government Request Principles</span></a><span
style='font-size:10.0pt;font-family:"Arial",sans-serif;color:#3D464D'> and </span><a
href="http://www.models4insight.com/transparency/reports" target="_blank"><span
style='font-size:10.0pt;font-family:"&amp;quot",serif;color:#0070E0;text-decoration:
none;text-underline:none'>Transparency Report</span></a><span style='font-size:
10.0pt;font-family:"Arial",sans-serif;color:#3D464D'> for more detailed
information on our approach and response to government requests. </span><span
style='font-family:"Times New Roman",serif;mso-bidi-font-family:"Times New Roman";
mso-bidi-theme-font:minor-bidi'></span></p>

<h2 style='margin-top:0cm;margin-right:0cm;margin-bottom:3.0pt;margin-left:
0cm;line-height:16.0pt'><span style='font-size:10.0pt;font-family:"&amp;quot",serif;
color:#3D464D'>How</span></h2>

<p style='margin-top:0cm;margin-right:0cm;margin-bottom:9.75pt;margin-left:
0cm;line-height:15.6pt'><em><span style='font-size:10.0pt;font-family:"&amp;quot",serif;
color:#3D464D'>Security</span></em><span style='font-size:10.0pt;font-family:
"&amp;quot",serif;color:#3D464D'>. We have a team dedicated to keeping your
information secure and testing for vulnerabilities. We also continue to work on
features to keep your information safe in addition to things like two-factor
authentication, encryption of files at rest, and alerts when new devices and
apps are linked to your account. </span></p>

<p style='margin-top:0cm;margin-right:0cm;margin-bottom:9.75pt;margin-left:
0cm;line-height:15.6pt'><em><span style='font-size:10.0pt;font-family:"&amp;quot",serif;
color:#3D464D'>Retention</span></em><span style='font-size:10.0pt;font-family:
"&amp;quot",serif;color:#3D464D'>. We'll retain information you store on our
Services for as long as we need it to provide you the Services. If you delete
your account, we'll also delete this information. But please note: (1) there
might be some latency in deleting this information from our servers and back-up
storage; and (2) we may retain this information if necessary to comply with our
legal obligations, resolve disputes, or enforce our agreements. You can access
your personal information by logging into your Models4Insight account. </span></p>

<h2 style='margin-top:0cm;margin-right:0cm;margin-bottom:3.0pt;margin-left:
0cm;line-height:16.0pt'><span style='font-size:10.0pt;font-family:"&amp;quot",serif;
color:#3D464D'>Where</span></h2>

<p style='margin-top:0cm;margin-right:0cm;margin-bottom:9.75pt;margin-left:
0cm;line-height:15.6pt'><em><span style='font-size:10.0pt;font-family:"&amp;quot",serif;
color:#3D464D'>Around the world</span></em><span style='font-size:10.0pt;
font-family:"&amp;quot",serif;color:#3D464D'>. To provide you with the
Services, we may store, process and transmit information in the United States
and locations around the world - including those outside your country.
Information may also be stored locally on the devices you use to access the
Services. </span></p>

<p style='margin-top:0cm;margin-right:0cm;margin-bottom:9.75pt;margin-left:
0cm;line-height:15.6pt'><span style='font-size:10.0pt;font-family:"&amp;quot",serif;
color:#3D464D'>When transferring data from the USA, European Union, the
European Economic Area, and Switzerland, Models4Insight relies upon a variety
of legal mechanisms, including contracts with our users. </span></p>

<p style='margin-top:0cm;margin-right:0cm;margin-bottom:9.75pt;margin-left:
0cm;line-height:15.6pt'><span style='font-size:10.0pt;font-family:"&amp;quot",serif;
color:#3D464D'>Models4Insight is subject to oversight by Dutch law about our
Privacy Shield compliance. We ask that you first submit any such complaints
directly to us via </span><a href="mailto:privacyshield@models4insight.com"><span
style='font-size:10.0pt;font-family:"&amp;quot",serif'>privacyshield@models4insight.com</span></a><span
style='font-size:10.0pt;font-family:"&amp;quot",serif;color:#3D464D'>. </span></p>

<h2 style='margin-top:0cm;margin-right:0cm;margin-bottom:3.0pt;margin-left:
0cm;line-height:16.0pt'><span style='font-size:10.0pt;font-family:"&amp;quot",serif;
color:#3D464D'>Changes</span></h2>

<p style='margin-top:0cm;margin-right:0cm;margin-bottom:9.75pt;margin-left:
0cm;line-height:15.6pt'><span style='font-size:10.0pt;font-family:"&amp;quot",serif;
color:#3D464D'>If we are involved in a reorganization, merger, acquisition or
sale of our assets, your information may be transferred as part of that deal. We
will notify you (for example, via a message to the email address associated
with your account) of any such deal and outline your choices in that event. </span></p>

<p style='margin-top:0cm;margin-right:0cm;margin-bottom:9.75pt;margin-left:
0cm;line-height:15.6pt'><span style='font-size:10.0pt;font-family:"&amp;quot",serif;
color:#3D464D'>We may revise this Privacy Policy from time to time, and will
post the most current version on our website. If a revision meaningfully
reduces your rights, we will notify you. </span></p>

<h2 style='margin-top:0cm;margin-right:0cm;margin-bottom:3.0pt;margin-left:
0cm;line-height:16.0pt'><span style='font-size:10.0pt;font-family:"&amp;quot",serif;
color:#3D464D'>Contact</span></h2>

<p style='margin-top:0cm;margin-right:0cm;margin-bottom:9.75pt;margin-left:
0cm;line-height:15.6pt'><span style='font-size:10.0pt;font-family:"&amp;quot",serif;
color:#3D464D'>Have questions or concerns about Models4Insight, our Services
and privacy? Contact us at </span><a href="mailto:privacy@models4insight.com"><span
style='font-size:10.0pt;font-family:"&amp;quot",serif'>privacy@models4insight.com</span></a><span
style='font-size:10.0pt;font-family:"&amp;quot",serif;color:#3D464D'>. </span></p>

<p class=MsoNormal></p>
            </section>
            <footer class="modal-card-foot">
                <button id="privacyGotIt" class="button is-success">I got it</button>
            </footer>
        </div>
    </div>
  </div>
</div>

<script>
    const tosModal = document.getElementById('tosModal');
    const privacyModal = document.getElementById('privacyModal');

    function toggleTOSModal() {
        return () => tosModal.classList.toggle('is-active');
    }

    function togglePrivacyModal(){
        return () => privacyModal.classList.toggle('is-active');
    }

    // Get the button that opens the modal
    const tosLink = document.getElementById("myTerms");
    const tosBackground = document.getElementById("tosBackground");
    const tosClose = document.getElementById("tosClose");
    const tosGotIt = document.getElementById("tosGotIt");

    const privacyLink = document.getElementById("myPrivacy");
    const privacyBackground = document.getElementById("privacyBackground");
    const privacyClose = document.getElementById("privacyClose");
    const privacyGotIt = document.getElementById("privacyGotIt");

    tosLink.onclick = toggleTOSModal();
    tosBackground.onclick = toggleTOSModal();
    tosClose.onclick = toggleTOSModal();
    tosGotIt.onclick = toggleTOSModal();

    privacyLink.onclick = togglePrivacyModal();
    privacyBackground.onclick = togglePrivacyModal();
    privacyClose.onclick = togglePrivacyModal();
    privacyGotIt.onclick = togglePrivacyModal();

    // Form validation for terms agreement and phone number
    const registrationForm = document.getElementById('kc-register-form');
    const termsCheckbox = document.getElementById('user.attributes.termsAgreement');
    const phoneInput = document.getElementById('user.attributes.phoneNumber');
    
    if (registrationForm && termsCheckbox) {
        registrationForm.addEventListener('submit', function(e) {
            let isValid = true;
            
            // Check terms agreement
            if (!termsCheckbox.checked) {
                e.preventDefault();
                alert('You must agree to the Terms of Service and Privacy Policy to register.');
                return false;
            }
            
            // Check phone number format if provided
            if (phoneInput && phoneInput.value.trim() !== '') {
                const phoneValue = phoneInput.value.trim();
                
                // Check length (5-20 characters)
                if (phoneValue.length < 5 || phoneValue.length > 20) {
                    e.preventDefault();
                    alert('Phone number must be between 5 and 20 characters long.');
                    phoneInput.focus();
                    return false;
                }
                
                // Check allowed characters: +, (), spaces, and numbers only
                const phonePattern = /^[\+\(\)\s\d]+$/;
                if (!phonePattern.test(phoneValue)) {
                    e.preventDefault();
                    alert('Phone number can only contain +, (), spaces, and numbers.');
                    phoneInput.focus();
                    return false;
                }
            }
        });
    }
</script>


</#if>  
</@layout.registrationLayout>
