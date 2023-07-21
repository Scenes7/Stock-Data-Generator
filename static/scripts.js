let namee = document.getElementById('name')
let price = document.getElementById('price')
let exchange = document.getElementById('exchange')
let industry = document.getElementById('industry')
let submitBtn = document.getElementById('submitBtn')
let tt = document.getElementById('testh')
let graphDiv = document.getElementById('bokeh-graph')
let errorMessage = document.getElementById('errorMessage')

let earnings = []; shares = []
for (let i = 1; i <= 4; i++) {
    earnings.push(document.getElementById('earning' + i))
    shares.push(document.getElementById('shares' + i))
}
//earnings, price, shares

exchange.addEventListener('change', () => {
})

submitBtn.addEventListener('click', (e) => {
    e.preventDefault();
    earningsValue = []; sharesValue = []

    for (let i = 0; i <= 3; i++) {
        if (earnings[i].value == 0 || shares[i].value == 0) break;
        earningsValue.push(earnings[i].value)
        sharesValue.push(shares[i].value)
    }
    chosenName = namee.value
    initialPrice = price.value
    selectedExchange = exchange.value
    selectedIndustry = industry.value

    url = "http://127.0.0.1:5000/submission"
    method = "POST"
    data = {
        name: chosenName,
        exchange: selectedExchange,
        industry: selectedIndustry,
        earnings: earningsValue,
        price: initialPrice,
        shares: sharesValue,
    }
    const headers = {
        'Content-Type': 'application/json'
      };
      

    sendHttpRequest(url, method, data, headers)
    .then(data => {
      if (!data) {
        errorMessage.innerHTML = "Make sure all basic information is filled out and at least 1 quarter is completed. All fields outside of basic information must be numeric."
        return
      }
      errorMessage.innerHTML = ""
      graphDiv.innerHTML = ""
      item = JSON.parse(data)
      Bokeh.embed.embed_item(item);
    })
        // .then(responseData => {
        //     tt.innerHTML = responseData
        //     // console.log('Response:', responseData);
        //     // console.log(responseData.statusText)
        // });

    // sending 6 things; 3 var, 3 arrays
})


function isNumeric(str) { // you check strings using this, but maybe do all the processing in python?
    if (typeof str != "string") return false
    return !isNaN(str) && // use type coercion to parse the _entirety_ of the string (`parseFloat` alone does not do this)...
        !isNaN(parseFloat(str)) // ...and ensure strings of whitespace fail
}

async function sendHttpRequest(url, method, data, headers) {

    const requestOptions = {
      method: method,
      headers: headers,
      body: JSON.stringify(data)
    };

    let response = await fetch(url, requestOptions);
    // return fetch(url, requestOptions)
    if (!response.ok) {
      return ""
    }
    let ret = await response.text()
    return ret

    // f.then(response => response.text())
    // .then(data => {
    //   return data;
    // })
    // .catch(error => {
    //   console.error('ErrorAAAAAAAAA:', error);
    // });
  }