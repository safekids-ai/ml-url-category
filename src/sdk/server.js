const express = require('express');
const AWS = require('aws-sdk');
const bodyParser = require('body-parser');
const app = express();
const port = 3000;

// Configure AWS
AWS.config.update({
  region: 'your-region',
  accessKeyId: 'YOUR_ACCESS_KEY_ID',
  secretAccessKey: 'YOUR_SECRET_ACCESS_KEY'
});

// Create Lambda service object
const lambda = new AWS.Lambda();

app.use(bodyParser.json());

app.post('/check-website', (req, res) => {
  const params = {
    FunctionName: 'your-lambda-function-name',
    Payload: JSON.stringify({ websiteUrl: req.body.websiteUrl }),
  };

  lambda.invoke(params, (err, data) => {
    if (err) {
      console.error(err);
      res.status(500).send('Error invoking Lambda function');
    } else {
      res.send(JSON.parse(data.Payload));
    }
  });
});

app.listen(port, () => {
  console.log(`Server is running on http://localhost:${port}`);
});
