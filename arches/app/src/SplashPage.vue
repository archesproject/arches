<template>

<div class="container">
  <header><h2>SF Project Title</h2></header>
    <nav>About | Search | Login | Translate</nav>
    <!-- **** reserve div for maintenance alerts  **** -->
        <alert>Mainteneance Alert</alert>
    <banner style="background-color: #fffad6;text-align: center;">Banner Image</banner>
        <message>SF Cultural Resources Map is in Beta &ndash; help us make it better!</message>
<main0>
  <p style="text-align: center">SF Cultural Resources lets you share and explore the significant places, people, organizations, and events that have shaped the diverse history of San Francisco.</p></main0>
    <cta><div class="flex">
        <div style="background-color: #b85000; color:#ffffff;text-align: center;padding:20px;border-top: solid 8px #ffffff;"><p style="color:#ffffff;font-weight:bold;margin-top:0px;font-size:1em;">Community Stories</p></div>
        <div style="background-color: #b85000; color:#ffffff;text-align: center;padding:20px;border-top: solid 8px #ffffff;"><p style="color:#ffffff;font-weight:bold;margin-top:0px;font-size:1em;">How-To Guides</p></div>
        <div style="background-color: #b85000; color:#ffffff;text-align: center;padding:20px;border-top: solid 8px #ffffff;"><p style="color:#ffffff;font-weight:bold;margin-top:0px;font-size:1em;">Map Search</p></div>
        </div>             </cta>
<main><div class="flex">
        <div style="background-color: #fffad6; color:#4d4d4d;text-align: center;padding:20px;min-height: 12em;border-bottom: 8px solid #ffffff;">Inner Sunset Neighborhood Commercial Districts</div>   
        <div style="background-color: #fffad6; color:#4d4d4d;text-align: center;padding:20px;min-height: 12em;border-bottom: 8px solid #ffffff;">Japantown and Fillmore Neighborhood Commercial Districts</div>   
</div> 
</main>
<main1><h2>Community Stories</h2>
<h2>About</h2>
<p>SF Cultural Resources is an online information management platform created specifically for documneting the findings of the San Francisco Citywide Cultural Resources Survey (SF Survey), which are reviewed by community members, San Francisco Planning, and the Histoic Preservation Commission.</p>
<p>SF Cultural Resources is the result of a partnership between the San Francisco Planning Department and the Getty Conservation Instittute, with the assistance of Farallon Geographics. It is powered by arches, an open-source heritagge data management platform developed by the Getty Conservation Instittute and the World Monuments Fund.</p>
<h2>How-To Guides</h2>
<p>Click on the thumbnails below to access the video and step-by-step PDF guides.</p>
<div class="flex">
        <div style="background-color: #b85000; color:#ffffff;text-align: center;padding:20px;border-top: solid 8px #ffffff;"><p style="color:#ffffff;font-weight:bold;font-size:1em;margin-top:0px;">Video Guide</p></div>
        <div style="background-color: #b85000; color:#ffffff;text-align: center;padding:20px;border-top: solid 8px #ffffff;"><p style="color:#ffffff;font-weight:bold;font-size:1em;margin-top:0px;">PDF Guide</p></div>
        </div></main1>
<main2>
  <h2 style="margin-top:-10px !important;">Contact</h2>
    <p>If you would like to get in contact with a staff member or provide feedback on the Beta SF Cultural Resources site, email <a href="mailto:CPC.Survey@sfgov.org">CPC.Survey@sfgov.org</a> or leave a voicemail at (628) 652-7573.</p>
    </main2>
  <footer><footer class="site-footer" role="contentinfo">
    <div class="flex">
        <div>
            <a href="https://sfplanniong.org" target="_blank" rel="noopener noreferrer">
                <div style="max-width:25em;"><img class="seal" src="https://sfplanning.org/themes/sfplanning/src/img/logo.png" alt="Logo of San Francisco Planning" style="max-width:100%;height:auto;"></div>
            </a>
            <ul>
                <li>© 2023 San Francisco Planning</li>
                <li><a href="/policies">Privacy Policies</a></li>
                <li><a href="/policies/accessibility">Accessibility</a></li>
            </ul>
        </div>
<div>
 <h3>Connect With Us</h3>           
<ul class="social-links">
    <li>Facebook  |  Twitter  |  YouTube  |  Flickr  |  Instagram</li>
</ul>
</div>
<div class="newsletter">
            <h3>Stay Informed</h3>
            <p>Provide your email address to sign up for news or other topics of interest. Unsubscribe at any time.</p>
            <form id="GD-snippet-form" action="https://public.govdelivery.com/accounts/CASFPD/subscriber/qualify?qsp=CASFPD_1" accept-charset="UTF-8" method="post" target="_blank"><input name="utf8" type="hidden" value="✓" /><input type="hidden" name="authenticity_token" value="JY1aOph71HM/7u0ikM3kYmKJ807OW+mShJy1Wr7fxN79Muq3URv4GuKYtSmzyNgUVZS2qcoYTZkK0UA7fhHC+g==" />
                <input type="text" name="email" id="email" placeholder="Your email address" />
                <input type="submit" name="commit" value="Sign Up" class="newsletter__submit" />
            </form>
</div>
</div>
</footer> </footer>
</div>
</template>

<style type="text/css" scoped>
/* https://codepen.io/SitePoint/pen/YzRMazK */
.container {
  display: grid;
  gap: 10px;
  grid-template-columns: 1fr 1fr 1fr 1fr;
  grid-template-rows: auto auto auto auto auto auto auto auto auto auto;
  grid-template-areas:
"header nav nav nav"
"alert  alert   alert  alert"
"banner  banner   banner  banner"
"message  message  message  message"
"main0  main0   main0   main0"
"cta  cta  cta  cta"
"main  main   main   main"
"main1  main1   main1   main1"
"main2  main2   main2   main2"
"main3  main3   main3   main3"
"footer footer footer footer";
}
header {
  grid-area: header;
}
nav {
    grid-area: nav;
    text-align:right;
    /*background-color: #E4E4E4;*/
}
banner {
  grid-area: banner;
    height: 30vh;
margin: 0px 40px;
}
alert {
  grid-area: alert;
        text-align: center;
  background-color: #D70003;
    color:#ffffff;
    margin:0px 40px -10px 40px;
    padding: 10px !important;
}
message {
  grid-area: message;
        text-align: center;
  background-color: #205493;
    color:#ffffff;
    margin:-10px 40px 0px 40px;
    padding: 10px !important;
}
cta {
  grid-area: cta;
  height: min-content;
  border: 8px solid #ffffff;
    padding: 12px;
}
main {
  grid-area: main;
  height: min-content;
    }
main0 {
  grid-area: main0;
  height: min-content;
}
main1 {
  grid-area: main1;
  height: min-content;
}
main2 {
  grid-area: main2;
  height: min-content;
}
main3 {
  grid-area: main;
  height: min-content;
    }
footer {
    grid-area: footer;
    background-color: #4D4D4D;
    padding: 5px !important;
}
/* non-essential styles */
.container {
  width: 100%;
  border: 10px solid white;
  background: white;
  color: black;
      padding: 10px 40px;
}
.container > * {
  background-color: none /*#EFEFEF*/;
  padding: 10px 40px;
  /*border: 0px solid #454545;*/
}
body {
  display: grid;
  place-items: center;
  min-height: 100vh;
  background-color: #30353b;
}
p{
    font-family: Helvetica, Arial, "sans-serif";
    font-size: 1em;
    margin-top: 0 !important;
    line-height: 1.25em;
    }
h2{
    font-family: Helvetica, Arial, "sans-serif";
    font-size: 1.5em;
    margin-top:20px !important;
    margin-bottom:0px !important;
    }
h3{
    font-family: Helvetica, Arial, "sans-serif";
    font-size: 1.35em;
    }
@media only screen and (max-width: 900px) {
.container {
  width: 100%;
    padding: 10px;
    }
.container > * {
  background-color: none /*#EFEFEF*/;
  padding: 0px;
  /*border: 0px solid #454545;*/
}
alert {
  grid-area: alert;
        text-align: center;
  background-color: #D70003;
    color:#ffffff;
    margin:0px 0px -10px 0px;
    padding: 10px !important;
}
    banner {
margin: 0px;
}
    message {
  grid-area: message;
        text-align: center;
  background-color: #205493;
    color:#ffffff;
    margin:-10px 0px 0px 0px;
        padding:10px !important;
}
.flex div {
    -ms-flex: 1;
    flex: 1;
    margin-right: 0px /*was 20px;; */;
}
    .site-footer h3 {
    margin-top: 1em;
        border-top: 1px solid #ffffff;
}
    }
* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}
</style>