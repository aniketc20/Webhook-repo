var old_top = '{{ old_top }}';;
setInterval(fetch, 15000);
function fetch() {
// Making the AJAX Request
    console.log(old_top);
    $.ajax({
            method: 'POST',
            url: '/fetch',
            data: {
                'old_top': old_top,
            },
            beforeSend: function (xhr) {
            xhr.setRequestHeader("X-CSRFToken", csrftoken);
            },
            success: function (data) {
                var data = JSON.parse(data);
                var dataItems = "";
                $.each(data, function (index) {
                date = new Date(data[index]['timestamp']).toUTCString().replace("GMT", "UTC");
                var timestamp = new Date(data[index]['timestamp']);
                hour = timestamp.getUTCHours()%12;
                mins = timestamp.getUTCMinutes();
                if(Math.floor(timestamp.getUTCHours()/12) > 0)
                {
                    if(mins<10)
                    {
                        mins = '0' + mins;
                    }
                    time = hour + ':' + mins + ' PM';
                }
                else
                {
                    if(mins<10)
                    {
                        mins = '0' + mins;
                    }
                    time = hour + ':' + mins + ' AM';
                }
                if(data[index]['action']=='pushed')
                {
                    dataItems += '<b>' + data[index]['author'] + ' ' + data[index]['action'] + '</b> to <b>' + 
                    data[index]['to_branch'] + '</b> on <b>' + date.slice(5, date.length-12) + '- ' + time + ' UTC</b><br><br>';
                }
                if(data[index]['action']=='pull-request')
                {
                    dataItems += '<b>' + data[index]['author'] + '</b> submitted a <b>' + data[index]['action'] + '</b> from <b> ' +
                    data[index]['from_branch'] + '</b> to <b>' + data[index]['to_branch'] + '</b> on <b>'+ date.slice(5, date.length-12) + '- ' + time + ' UTC</b><br><br>';
                }
                if(data[index]['action']=='merged')
                {
                    dataItems += '<b>' + data[index]['author'] + ' ' + data[index]['action'] + '</b> branch <b>' + data[index]['from_branch'] + 
                    '</b> to <b>' + data[index]['to_branch'] + '</b> on <b>' + date.slice(5, date.length-12) + '- ' + time + ' UTC</b><br><br>';
                }
                });
                if(data.length>1)
                {
                    old_top = data[1]['new_top'];
                }
            if(dataItems=="")
            {
                $("p").html("No updates in the past 15 seconds");
            }
            else
            {
                $("p").html(dataItems);
            }
            },
            error: function (error) {
                console.log(error);
            }
        });
    }