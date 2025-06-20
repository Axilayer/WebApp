function authentication(){
    //Create references to the input elements we wish to validate
    var username = document.getElementById("username");
    var password = document.getElementById("password");
    //Check if username field is empty
    if(username.value != "@Axilayer2024" || password.value !="Customer$2025"){
            alert("Either your password or username is incorrect");
            username.focus();
            password.focus();
            return false;
    } else if (username.value == "" || password !=""){
        alert("Please enter your crendtials");
            username.focus();
            password.focus();
            return false;
    } else if(username.value == "@Axilayer2024" || password.value =="Customer$2025"){
        window.location.href("dashboard.html")
    } else {
        username.focus();
        password.focus();
    }

}