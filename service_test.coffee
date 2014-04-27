####################
# Test script to generated thumbnail using node and request module.
#
# Usage:
#   npm install request
#   coffee service_test.coffee <path to file> <dest thumbnail>
# 
# Thumbnail PNG will be saved to: thumbnail.png

request  = require 'request'
path 	 = require 'path' 
fs 		 = require 'fs'

thumbnailer_url = "http://localhost:8001"

make_file_thumbnail = (src_path, dest_stream, cb) ->

	# knownLength of the file must be passed to the form
	# Us fs.stat to get it in stats.size	
	fs.stat src_path, (err, stats) ->

		r = request.post {url: thumbnailer_url, encoding: null, headers: {"Accept-Encoding": "gzip, deflate, compress"}}, (err, res, body) ->
			if err or res.statusCode != 200
				if err then console.log "ERROR: #{err}"
				if cb then cb(body)
			
		# Build the file upload form, passing the readStream, filename and knownLength.
		form = r.form()
		form.append('thumbnail', 'yes')
		form.append('thumbnail_size', '500x500')
		form.append 'file', fs.createReadStream(src_path),
			filename: path.basename(src_path)			
			knownLength: stats.size

		# Pipe the response to the given dest stream.
		r.pipe dest_stream

		# When download is complete, call the callback.
		dest_stream.on 'finish', () ->		
			if cb then cb(r.response)

if require.main == module
	if process.argv.length != 4
		console.log "Usage: #{path.basename(process.argv[1])} <src file> <dest thumbnail>"
		process.exit(1)

	src_path = process.argv[2]
	dest_path = process.argv[3]

	dest_stream = fs.createWriteStream dest_path, {flags: 'w', encoding: null}

	make_file_thumbnail src_path, dest_stream, (response) ->
		console.log "Thumbnail saved to: #{dest_stream.path}"
		process.exit 0