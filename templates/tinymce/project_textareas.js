tinyMCE.init({
    // selector: "#id_project-content,#id_content",
    theme: "advanced",
    plugins: ["image"],
    theme_advanced_buttons3_add : "preview",
    language: "{{ language }}",
    directionality: "{{ directionality }}",
    spellchecker_languages : "{{ spellchecker_languages }}",
    spellchecker_rpc_url : "{{ spellchecker_rpc_url }}",
    file_browser_callback: function(field_name, url, type, win) {
        if(type=='image') $('#my_form input').click();
    }
});