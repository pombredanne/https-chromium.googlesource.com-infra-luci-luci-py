const { commonBuilder } = require('pulito');
const path = require('path');

module.exports = commonBuilder(__dirname);

module.exports.module.rules.push({
	test: /.js$/,
	use: [
		{
			loader: path.resolve('html-template-minifier/loader.js'),
			options: {
				alpha: 'beta',
			},
		},
	]
})