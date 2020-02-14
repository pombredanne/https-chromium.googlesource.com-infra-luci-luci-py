# LUCI Config UI

This is a UI for the configuration service.


## Setting up

*	First, make sure you have the [Polymer CLI](https://polymer-library.polymer-project.org/3.0/docs/tools/polymer-cli) installed.

* Install [Google App Engine SDK](https://cloud.google.com/appengine/downloads).

*	Run `polymer install` in the ui directory to make sure you have all the dependencies installed. It is expected to pull all the dependency packages under *node_modules* directory from npm. If no *node_modules* directory gets generated after running the command, run `npm install` instead.

## Running locally

*	First, change all the URLs in the iron-ajax elements. Simply add "https://luci-config.appspot.com" before each URL.
	*	One in src/config-ui/front-page.html
	*	Two in src/config-ui/config-set.html
	*	One in src/config-ui/config-ui.html

*	Run `polymer build` in the ui directory to build the ui app

*	In the config-service folder run `dev_appserver.py app.yaml`

*	Visit [http://localhost:8080](http://localhost:8080)


## Running Tests

*	Your application is already set up to be tested via [web-component-tester](https://github.com/Polymer/web-component-tester).
	Run `wct`, `wct -p` or `polymer test` inside ui folder to run your application's test suites locally.
	These commands will run tests for all browsers installed on your computer.

## Deploy

* Finish all steps mentioned in [Setting up](#setting-up) section.
* Run `polymer build` in the *ui* directory to build the ui app.
* Check if *node_modules* directory and *build* directory is present under *ui* directory and the build artifacts is under the *default* directory in *build* directory.
* Use the `gae.py` script to deploy.
