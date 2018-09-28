function change_to_resolution(){
    document.getElementById("input-box-form").action = '{{ url_for(\'resolution\') }}';
}

function change_to_eval(){
    document.getElementById("input-box-form").action = '\{\{ url_for(\'resultado\') \}\}';
}