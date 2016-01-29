fs = require('fs');
http = require('http');
url = require('url');

// Read in the question and survey response data
var personJSON = fs.readFileSync('data/persons.json', 'utf8');
var personData = JSON.parse(personJSON);
var questionJSON = fs.readFileSync('data/questions.json', 'utf8');
var questionData = JSON.parse(questionJSON);

var valid_queries = require('./valid_queries.json');
var img = fs.readFileSync('./favicon.ico');
var simple_cache = {};

function processValidRequest(category_var, comparison_var) {

    // Support caching for faster response times/avoid aggregation computations
    // var memo_key = category_var + '-' + comparison_var;
    // if(memo_key in simple_cache) {
    //   return simple_cache;
    // } else if (Object.keys(simple_cache).length == 10) {
    //   delete simple_cache[memo_key];
    // }

    // Extract the possible responses from question.json
    var categories = questionData[category_var][5];
    var comparison_values = questionData[comparison_var][5];
    // In the case the comparison and category variable values are a tuple
    if (Array.isArray(categories[1])) {
        categories = categories[1];
    }

    if (Array.isArray(comparison_values[1])) {
        comparison_values = comparison_values[1];
    }
    var n = personData.length; // number of survey respondees
    var m = categories.length; // number of categories
    
    // Aggregate counts for selected variables and store into data[]
    // in specified format (see an example query for format)
    var out_data = [];
    for (category_index = 0; category_index < categories.length; category_index++) {
        out_data.push({
            category: categories[category_index]
        });
        var series_array = [];
        for (k = 0; k < comparison_values.length; k++) {
            var counts = [];
            // Initialize the counts
            for (var c = 0; c < categories.length; c++) {
                counts.push(0);
            }
            var current_comp_value = comparison_values[k];
            
            //Find frequencies
            var totalOrgs = 0
            for (i = 0; i < personData.length; i++) {
                if (personData[i][comparison_var].indexOf(
                    current_comp_value) >= 0) {
                    totalOrgs += 1;
                    for (j = 0; j < categories.length; j++) {
                        if (personData[i][category_var] == categories[j])
                            counts[j] += 1;
                    }
                }
            }
            series_array.push({
                name: comparison_values[k],
                value: (counts[category_index] / totalOrgs)
            });
        }
        for (k = 0; k < series_array.length; k++) {
            out_data[category_index][series_array[k].name] = series_array[k]
                .value;
        }
        out_data[category_index]["series"] = series_array;
    }

    // simple_cache[memo_key] = out_data;
    return out_data;
}

var json_headers = {
    'Access-Control-Allow-Origin': '*',
    'Content-Type': 'application/json'
};
var plain_headers = {
    'Access-Control-Allow-Origin': '*',
    'Content-Type': 'text/plain'
};
var image_headers = {
    'Access-Control-Allow-Origin': '*',
    'Content-Type': 'image/jpeg'
};

http.createServer(function(req, res) {
    var request = url.parse(req.url, true);
    var pieces = request.pathname.substring(1).split('-');
    // Return the site favicon!
    if (pieces[0] == 'favicon.ico') {
        res.writeHead(200, image_headers);
        res.end(img, 'binary');
    }
    // If the request is not hyphenated or formed incorrectly
    if (pieces.length != 2) {
        res.writeHead(200, plain_headers);
        res.end('Malformed request!\n');
    } else {
        var var1 = pieces[0];
        var var2 = pieces[1];
        if ((!(var1 in valid_queries)) || (!(var2 in valid_queries))) {
            res.writeHead(200, plain_headers);
            res.end('Request parameters not recognized!\n');
        } else {
            var json = processValidRequest(var1, var2);
            res.writeHead(200, json_headers);
            res.end(JSON.stringify(json));
        }
    }
}).listen(process.env.PORT || 8080);
