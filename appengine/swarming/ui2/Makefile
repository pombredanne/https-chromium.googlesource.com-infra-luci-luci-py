default: package-lock.json
	npx webpack --mode=development

release: package-lock.json
	npx webpack --mode=production
	cp node_modules/@webcomponents/custom-elements/custom-elements.min.js dist/custom-elements.min.js

serve: package-lock.json
	npx webpack-dev-server --mode=development --watch-poll

test:
	# Run the generated tests just once under Xvfb.
	xvfb-run --auto-servernum --server-args "-screen 0 1280x1024x24" npx karma start

test_browser:
	# Starts up the server so one can navigate to http://0.0.0.0:9876 and run the
	# tests there, seeing the results. Unfortunately, due to how karma needs to
	# concatenate the _test.js files and run them through webpack, it doesn't
	# autodetect changes and needs to be re-run manually :(
	xvfb-run --auto-servernum --server-args "-screen 0 1280x1024x24" npx karma start --no-single-run

package-lock.json: package.json
	npm install
