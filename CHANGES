Version History
===============

Version 0.5.11
--------------
* Fix: CAPTCHA_TEST_MODE was broken. (#163, thanks @ohlr for reporting)


Version 0.5.10
--------------
* Test against Django 2.2a1
* Docs: Grammar correction (#160, thanks @DanAtShenTech)
* Fix: Add '+' to text replacement for audio support (#157, thanks @geirkairam)
* I18N: Added Swedish translation (#155, thanks @stefannorman)
* Docs: Provide an example of custom field template (#158, thanks @TheBuky)


Version 0.5.9
-------------
* Add missing Jinja2 templates in the pypi packages.


Version 0.5.8
-------------
* Add support for Jinja2 templates (Issue #145, PR #146, thanks @ziima)
* Cleanup, drop dependency on South (#141, #142 thanks @ziima)


Version 0.5.7
-------------
* Use templates for rendering of widgets (Issue #128, #134, PR #133, #139, thanks @ziima)
* Always defined audio context variable  (PR #132, thanks @ziima)
* Test against Django 2.1a
* Updated AJAX update docs (PR #140, thanks @CNmanyue)
* Fixed a typo in a variable name (PR #130, thanks @galeo)


Version 0.5.6
-------------
* Updated render method to adapt for Django 2.1 (PR #120, thanks @skozan)
* Improved compatibility with Django 2.0, tests against Django 2.0a1 (PR #121, thanks @Kondou-ger)
* Dropped support for PIL (use Pillow instead)
* Updated documentation (Fixes #122, thanks @claudep)
* Test against Django 2.0b1
* Return a Ranged Response when returning WAV audio to support Safari (Fixes #123, thanks @po5i)
* Optionally inject brown noise into the generated WAV audio file, to avoid rainbow-table attacks (Fixes #124, thanks @appleorange1)
* Test against Django 2.0


Version 0.5.5
-------------
* I messed the 0.5.4 release, re-releasing as 0.5.5

Version 0.5.4
-------------
* Removed a couple gremlins (PR #113, thanks @Pawamoy)
* Added autocapitalize="off", autocorrect="off" and spellcheck="false" to the genreated field (PR #116, thanks @rdonnelly)
* Test against Django 1.11
* Drop support of Django 1.7 ("it'll probably still work")

Version 0.5.3
-------------
* Ability to pass a per-field challenge generator function (Fixes #109)
* Added a feature to get captchas from a data pool of pre-created captchas (PR #110, thanks @skozan)
* Cleanup to remove old code handling timezones for no longer supported Django versions
* Fix for "Size must be a tuple" issue with Pillow 3.4.0 (Fixes #111)

Version 0.5.2
-------------
* Use any mutliplication uperator instead of "*". (Fixes #77 via PR #104, thanks @honsdomi and @isergey)
* Test against Django 1.10

Version 0.5.1
-------------
* Fine tuning MANIFEST.in
* Prevent testproject from installing into site-packages

Version 0.5.0
-------------
* Adds missing includes in MANIFEST.in

Version 0.4.7
-------------
* Supported Django versions are now 1.7, 1.8 and 1.9
* Trying to fix the TravisCI build errors
* Use Django templates to render the individual fields, as well as the assembled Captcha Field (Issue #31)


Version 0.4.6
-------------
* Fixes an UnicodeDecodeError which was apparently only triggered during testing on TravisCI (I hope)
* Support for Django 2.0 urlpatterns syntax (PR #82, Thanks @R3v1L)
* settings.CAPTCHA_FONT_PATH may be a list, in which case a font is picked randomly (Issue #51 fixed in PR #88, Thanks @inflrscns)

Version 0.4.5
-------------
* Test with tox
* Test against Django 1.8 final
* Added ability to force a fixed image size (PR #76, Thanks @superqwer)

Version 0.4.4
-------------
* Added id_prefix argument (fixes issue #37)

Version 0.4.3
-------------
* Add null noise helper (Thanks @xrmx)
* Test against Django 1.7b4
* Added Spanish translations (Thanks @dragosdobrota)
* Massive cleanup (pep8, translations)
* Support for transparent background color. (Thanks @curaloucura)
* Support both Django 1.7 migrations and South migrations.
  Please note, you *must* add the following to your settings, if you are
  using South migrations and Django 1.6 or lower.
* Make sure autocomplete="off" is only applied to the text input, not the hidden input (Issue #68, thanks @narrowfail)
* Fixed some grammar in the documentation. (Thanks @rikrian)
* Return an HTTP 410 GONE error code for expired captcha images, to avoid crawlers from trying to reindex them (PR #70, thanks @joshuajonah)
* Fixed title markup in documentation (#74, thanks @pavlov99)
* Test against Django 1.7.1

Version 0.4.2
-------------
* Added autocomplete="off" to the input (Issue #57, thanks @Vincent-Vega)
* Fixed the format (msgfmt -c) of most PO and MO files distributed with the project
* Added Bulgarian translations. (Thanks @vstoykov)
* Added Japanese translations. (Thanks, Keisuke URAGO)
* Added Ukrainian translations. (Thanks, @FuriousCoder)
* Added support for Python 3.2. (Thanks, @amrhassan)

Version 0.4.1
-------------
* Dropped support for Django 1.3
* Fixed support of newer versions of Pillow (2.1 and above. Pillow 2.2.2 is now required) Thanks @viaregio (Issue #50)

Version 0.4.0
-------------
* Perfom some tests at package installation, to check whether PIL or Pillow are already installed. (Issue #46)
* Added Slovak translations. (Thanks @ciklysta)

Version 0.3.9
-------------
* Run most tests both with a regular Form and a ModelForm, to avoid regressions such as Issue #40
* Handle the special case where CaptchaFields are instantiated with required=False (Issue #42, thanks @DrMeers)
* Fixed a misspelled setting, we now support both spellings, but the docs suggest the correct one (Issue #36, thanks @sayadn)
* Added Django 1.6b to testrunner and adapted the test cases to support Django 1.6's new test discovery
* Added German translations. (Thanks @digi604)
* Frozen the version of Pillow to 2.0.0, as 2.1.0 seems to be truncating the output image -- Issue #44, Thanks @andruby
* Added Polish translations. (Thanks @stilzdev)

Version 0.3.8
-------------
* Fixed a critical bug (Issue #40) that would generate two captcha objects, and the test would always fail. Thanks @pengqi for the heads-up.


Version 0.3.7
-------------
* Improved Django 1.5 and Django HEAD (1.6) compatibility (thanks @uruz)
* Python3 compatibility (requires six and Pillow >= 2.0)
* Added zh_CN localization (thanks @mingchen)
* Make sure the generated challenge is a string type (the math challenge was probably broken -- Issue #33, thanks @YDS19872712)
* Massive cleanup and refactoring (Issue #38, thanks @tepez)
* Test refactoring to test a couple generators that weren't tested by default

Version 0.3.6
-------------
* Django 1.5 compatibility (only affects tests)
* Italian localization (thanks @arjunadeltoso)
* Russian localization (thanks @mikek)
* Fixed issue #17 - Append content-length to response (thanks @shchemelevev)
* Merged PR #19 - AJAX refresh of captcha (thanks @artofhuman)
* Merged PR #22 - Use op.popen instead of subprocess.call to generate the audio CAPTCHA (thanks @beda42)
* Fixed issue #10 - uniformize spelling of "CAPTCHA" (thanks @mikek)
* Fixed issue #12 - Raise error when try to initialize CaptchaTextInput alone and/or when try to initialize CaptchaField with widget keyword argument (thanks @vstoykov)
* Merged PR #15 - Allow a 'test mode' where the string 'PASSED' always validates the CAPTCHA (thanks @beda42)
* Dutch translation (thanks @leonderijke)
* Turkish translation (thanks @gkmngrgn)

Version 0.3.5
-------------
* Fixes issue #4: Fixes id_for_label malfunction with prefixed forms (thanks @lolek09)

Version 0.3.4
-------------
* Fixes issue #3: regression on Django 1.4 when USE_TZ is False

Version 0.3.3
-------------
* Django 1.4 Time zones compatibility
* PEP 8 love

Version 0.3.2
-------------
* Added a test project to run tests
* Added South migrations
