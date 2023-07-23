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
})


function isNumeric(str) { 
    if (typeof str != "string") return false
    return !isNaN(str) && !isNaN(parseFloat(str))
}

async function sendHttpRequest(url, method, data, headers) {

    const requestOptions = {
      method: method,
      headers: headers,
      body: JSON.stringify(data)
    };

    let response = await fetch(url, requestOptions);
    if (!response.ok) {
      return ""
    }
    let ret = await response.text()
    return ret

  }