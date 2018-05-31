default: package-lock.json
	npx webpack --mode=development

release: package-lock.json
	npx webpack --mode=production
	wget -O dist/custom-elements.min.js https://cdnjs.cloudflare.com/ajax/libs/custom-elements/1.0.8/custom-elements.min.js

serve: package-lock.json
	npx webpack-dev-server --mode=development --watch-poll

package-lock.json: package.json
	npm install
