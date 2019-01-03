"use strict";

/**
* Run this on windows desktop
* then browse (using google chrome/firefox) to http://[pi ip]:8080/
*/

const http = require('http');
const express = require('express');
const spawn = require('child_process').spawn

// Ancient piece of shit.
// const BinaryServer = require('binaryjs').BinaryServer;

const WebStreamerServer = require('./lib/ffmpeg');

const app = express();

//public website
app.use(express.static(__dirname + '/public'));
app.use(express.static(__dirname + '/vendor/dist'));


const server = http.createServer(app);
const silence = new WebStreamerServer(server, {
  width: 640,
  height: 480,
  fps: 24
});

var ps = null;


// Audio: server --> client;
const audio_server = http.createServer(function (req, res) {
  //url /audio.wav starts streaming from usb mic
  if (req.url === '/audio.wav') {
    console.log('Request for audio file');

    //if command is not started, start it
    if (ps === null) {
      res.writeHead(200, { 'Content-Type': 'audio/wav' });

      console.log('Spawning arecord');
      ps = spawn('arecord', ['-f', 'cd']);
      // ps = spawn('arecord',['-D','hw:1,0','-f','dat']);

      ps.stderr.on('data', function (data) {
        console.log('stderr: ' + data);
      });

      ps.stdout.on('data', function (data) {
        // console.log('sending data to client');
        res.write(data);
      });

      ps.on('exit', function (code) {
        if (ps)
          ps.kill('SIGHUP');
        ps = null;
        res.end();
        console.log('child process exited with code ' + code);
      });

      res.on('end', function () {
        console.log('End of stream');
      });

      res.on('close', function () {
        console.log('stream got closed by client');
        //end it if stream gets closed.
        ps.kill('SIGHUP');
        // ps = null;
      });

    } else {
      // TODO: Just kill this motherfucker who took the mic.
      console.log('USB mic already taken');
      res.writeHead(503, { 'Content-Type': 'text/html' });
      res.end('<html><head><title>Service Unavailable</title></head><body>Mic stream is already taken.</body></html>');
    }
  } else if (req.url === '/kill' && ps !== null) {
    console.log('Killing arecord');
    res.writeHead(302, { 'Location': '/' });
    ps.kill();
    res.end();
  } else {
    // For testing.
    res.writeHead(200, { 'Content-Type': 'text/html' });
    res.write('<!DOCTYPE html>');
    res.write('<html>');
    res.write('<head>');
    res.write('<title>Simple MIC Stream</title>');
    res.write('</head>');
    res.write('<body>');
    res.write('<audio src="/audio.wav" preload="none" controls>');
    res.write('</audio>');
    res.write('</body>');
    res.write('</html>');
    res.end();
  }
});



server.listen(8080);
audio_server.listen(8081);



// const Speaker = require('speaker');
 
// // Create the Speaker instance
// const speaker = new Speaker({
//   channels: 2,          // 2 channels
//   bitDepth: 16,         // 16-bit samples
//   sampleRate: 44100     // 44,100 Hz sample rate
// });



// // 
// const audio_client = new BinaryServer({ port: 8082 });
// audio_client.on('connection', function(client){
//   client.on('stream', function(stream, meta){
//       stream.on('data', function(data){
//           speaker.write(data);
//       });
//   });
// });
