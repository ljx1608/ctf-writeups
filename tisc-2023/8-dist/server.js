const express = require('express');
const app = express();
const port = 3000;

const db = require('./db');

const AWS = require('aws-sdk');
process.env.AWS_SDK_LOAD_CONFIG = 1;

AWS.config.getCredentials((err) => {
    if (err) console.log(err.stack);
    // TODO: Add more comments here
    else {
        console.log("Access key:", AWS.config.credentials.accessKeyId);
        console.log("Region:", AWS.config.region);
    }
});

const lambda = new AWS.Lambda();

const session = require('express-session');
const flash = require('connect-flash');
const bodyParser = require('body-parser');

app.use(session({
    secret: 'mysecret',
    resave: true,
    saveUninitialized: true
}));

app.use(flash());

var pug = require('pug')
app.set('view engine', 'pug');

var toolsObj = {};

toolsObj.saveFlash = function(req, res) {
    res.locals.errors = req.flash("error");
    res.locals.successes = req.flash("success");
};

module.exports = toolsObj;

app.use(bodyParser.urlencoded({
    extended: true
}));

app.get('/', (req, res) => {
    res.send(pug.renderFile('login.pug', {
        messages: req.flash()
    }));
});

app.get('/reminder', (req, res) => {
    const username = req.query.username;
    res.send(pug.renderFile('reminder.pug', { username }));
});

app.get('/remind', (req, res) => {
    const username = req.query.username;
    const reminder = req.query.reminder;
    res.send(pug.renderFile('remind.pug', { username, reminder }));
});

app.post('/api/submit-reminder', (req, res) => {
    const username = req.body.username;
    const reminder = req.body.reminder;
    const viewType = req.body.viewType;
    res.send(pug.renderFile(viewType, { username, reminder }));
});

app.post('/api/login', (req, res) => {
    // pk> Note: added URL decoding so people can use a wider range of characters for their username :)
    // dr> Are you crazy? This is dangerous. I've added a blacklist to the lambda function to prevent any possible attacks.

    const username = req.body.username;
    const password = req.body.password;
    if (!username || !password) {
        req.flash('error', "No username/password received");
        req.session.save(() => {
            res.redirect('/');
        });
    }

    const payload = JSON.stringify({
        username,
        password
    });

    try {
        lambda.invoke({
            FunctionName: 'craft_query',
            Payload: payload
        }, (err, data) => {
            if (err) {
                req.flash('error', 'Uh oh. Something went wrong.');
                req.session.save(() => {
                    res.redirect('/');
                });
            } else {
                const responsePayload = JSON.parse(data.Payload);
                const result = responsePayload;

                if (result !== "Blacklisted!") {
                    const sql = result;
                    db.query(sql, (err, results) => {
                        if (err) {
                            req.flash('error', 'Uh oh. Something went wrong.');
                            req.session.save(() => {
                                res.redirect('/');
                            });
                        } else if (results.length !== 0) {
                            res.redirect(`/reminder?username=${username}`);
                        } else {
                            req.flash('error', 'Invalid username/password');
                            req.session.save(() => {
                                res.redirect('/');
                            });
                        }
                    });
                } else {
                    req.flash('error', 'Blacklisted');
                    req.session.save(() => {
                        res.redirect('/');
                    });
                }
            }
        });

    } catch (error) {
        console.log(error)
        req.flash('error', 'Uh oh. Something went wrong.');
        req.session.save(() => {
            res.redirect('/');
        });
    }
});

app.listen(port, () => {
    console.log(`Server listening at http://localhost:${port}`);
});