document.addEventListener('DOMContentLoaded', () => { /*===== FOCUS =====*/
    document.getElementById('json').addEventListener('change', () => {
        var hidden = document.getElementById('void')
        if (hidden.name == "option") {
            hidden.name = "void"
        } else {
            hidden.name = "option"
        }

    })
})