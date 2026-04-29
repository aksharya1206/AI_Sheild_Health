document.getElementById("symptomForm").addEventListener("submit", function(e){

e.preventDefault()

let formData = new FormData(this)

fetch("/predict",{
method:"POST",
body:formData
})

.then(res => res.json())
.then(data => {

document.getElementById("result").innerText =
"Possible Disease: " + data.disease

})

})





document.getElementById("medicineForm").addEventListener("submit", function(e){

e.preventDefault()

let formData = new FormData(this)

fetch("/scan_medicine",{
method:"POST",
body:formData
})

.then(res => res.json())
.then(data => {

document.getElementById("medicineResult").innerText =
data.result + " | " + data.side_effects

})
})