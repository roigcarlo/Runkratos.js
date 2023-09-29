const express = require('express');
const cors = require('cors');
const fs = require('fs');

// Not used yet, for mdpa
// const multer = require('multer');

// var upload = multer({ dest: __dirname + '/public/uploads/' });
// var type = upload.single('upl');

var app = express();

app.use(cors());
app.use(express.json());

const port = 8288;

app.post('/upload_json', (req, res) => {
    fs.writeFile("public/ProjectParameters.json", JSON.stringify(req.body, null, 2), function(err) {
        if(err) { return console.log(err); }
    }); 

    res.sendStatus(200);
});

// Testing chield spawn + stream
app.get('/run_simulation', async (req, res) => {
    var spawn = require('child_process').spawn;
    let process_env = {
        'env': {
            'LD_LIBRARY_PATH'   : '/home/roigcarlo/Kratos/bin/Debug/libs', 
            'PYTHONPATH'        : '/home/roigcarlo/Kratos/bin/Debug'
        },
        'cwd': 'public/'
    }

    var child = spawn('python', ['MainKratos.py'], process_env);

    child.stdout.setEncoding('utf8');
    child.stdout.on('data', function(data) {
        console.log('stdout: ' + data);
        res.write(`${data}`);
    });

    child.stderr.setEncoding('utf8');
    child.stderr.on('data', function(data) {
        console.log('stderr: ' + data);
        res.write(`${data}`);
    });

    child.on('close', function(code) {
        console.log('closing code: ' + code);
        console.log('Full output of script: ');
    });
})

app.post('/kratos_lamma', (req, res) => {
    var spawn = require('child_process').spawn;
    let process_env = {
        'cwd': '/home/roigcarlo/Llama'
    }

    console.log("Got a llama request:", req.body)

    var child = spawn('/home/roigcarlo/Auto1111/venv/bin/python', ['run_llama.py', `${req.body}`], process_env);

    child.stdout.setEncoding('utf8');
    child.stdout.on('data', function(data) {
        console.log(`Got a llama response:\n${data}`);
        res.write(`${data}`);
    });

    child.stderr.setEncoding('utf8');
    child.stderr.on('data', function(data) {
        console.log("Error:", `${data}`)
        // res.write(`${data}`);
    });

    child.on('close', function(code) {
        res.end();
    });
}) 

// Testing strems
app.get('/stream', async (req, res) => {
    res.writeHead(200, {
        'Content-Type': 'text/plain; charset=utf-8',
        'Transfer-Encoding': 'chunked',
        'X-Content-Type-Options': 'nosniff'
    });
 
    const interval = setInterval(() => {
        const data1 = Math.random().toString(36).substring(2, 8);
        const data2 = Math.random().toString(36).substring(2, 8);
        res.write(`${data1} ${data2}`);
    }, 2000);
 
    setTimeout(() => {
        clearInterval(interval);
        res.end();
    }, 10000);
})

// Testing Response
app.get('/', (req, res) => {
  res.send('Hello World!')
})

app.listen(port, () => {
  console.log(`Example app listening on port ${port}`)
})