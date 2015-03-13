    $('form').submit(function(){
        var required = $('[required]'); // change to [required] if not using true option as part of the attribute as it is not really needed.
        var error = false;

        for(var i = 0; i <= (required.length - 1);i++)
        {
            if(required[i].value == '') // tests that each required value does not equal blank, you could put in more stringent checks here if you wish.
            {
                required[i].style.backgroundColor = 'rgb(255,155,155)';
                error = true; // if any inputs fail validation then the error variable will be set to true;
            }
        }

        if(error) // if error is true;
        {
            return false; // stop the form from being submitted.
        }
    });
