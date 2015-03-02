$( document ).ready(function()
{
    $( "#form-report" ).hide();
    $("#report-confirmation").hide();

	var elements = document.getElementsByClassName('label-like');
	for (var i = 0; i < elements.length; i++)
	{
		var data = parseInt(elements[i].innerHTML);
		if (data > 0)
			elements[i].style.color = "green";
		else if (data == 0)
			elements[i].style.color = "black";
		else
			elements[i].style.color = "red";
	}
});



function reply_message(id_message, author)
{
     $.ajax(
     {
        url: 'reply',
        type: 'get',
        data: 'message=' + id_message,
        success: function(data)
        {
            var editor = tinymce.activeEditor; 
            var content = editor.getContent();
            var new_content = '<p><strong>' + author + ' a dit: </strong></p>' +  '<blockquote>' + data + '</blockquote><br><br>';
            content += new_content;
            editor.setContent(content);
        },
    });
}

function like_message(id_message)
{
     $.ajax(
     {
        url: 'like',
        type: 'get',
        data: 'message=' + id_message,
        success: function(data)
        {
        	var label = document.getElementById('label '+ id_message);
			var like = parseInt(data);
        	if (like > 0)
        		label.style.color = "green";
        	else if (like == 0)
        		label.style.color = "black";
            else
                label.style.color = "red";
        	label.innerHTML = data;
        },
    });
}

function dislike_message(id_message)
{
     $.ajax(
     {
        url: 'dislike',
        type: 'get',
        data: 'message=' + id_message,
        success: function(data)
        {
        	var label = document.getElementById('label '+ id_message);
        	var like = parseInt(data);
        	if (like < 0)
        		label.style.color = "red";
        	else if (like == 0)
        		label.style.color = "black";
            else
                label.style.color = "green";
        	label.innerHTML = data;
        },
    });
}

function report_message(id_message, author)
{
    $( "#form-report" ).dialog(
    {
        open: function()
        {
            $( this ).find("#reason").css("width", "570px");
            $( this ).find("#reason").val("");
        },
        resizable: false,
        height: 230,
        width: 600,
        modal: true,
        buttons:
        [{
            text: "Annuler",
            click: function()
            {
                $( this ).dialog( "close" );
            }
        },
        {
            text: "Signaler",
            click: function()
            {
                var $this = $(this);
                $.ajax(
                     {
                        url: 'report',
                        type: 'get',
                        data: {'message': id_message, 'reason': $(this).find("#reason").val()},
                        success: function(data)
                        {
                            $("#report-confirmation").show();
                            $this.dialog( "close" );
                        },
                    });
            }
        }]
    });
}