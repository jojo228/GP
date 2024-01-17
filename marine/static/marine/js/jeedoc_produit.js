document.addEventListener('DOMContentLoaded', () => {

    // adding new element to bill

    // update the value of the final total
    let total = 0
    document.querySelectorAll('.montant').forEach(element => {
        total = total + Number(element.innerHTML);
    });
    document.querySelector('#total').innerHTML = total
})