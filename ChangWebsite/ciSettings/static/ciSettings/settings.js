/*
 * @Author: AChangAZha
 * @Date: 2022-08-28 21:07:01
 * @LastEditTime: 2022-08-29 13:52:19
 * @LastEditors: AChangAZha
 */
function getQuery(q) {
    return (window.location.search.match(new RegExp('[?&]' + q + '=([^&]+)')) || [, null])[1];
}
$(function () {
    var $toast = $('#js_toast');
    var code = getQuery("code")
    var csrftoken = $('input[name="csrfmiddlewaretoken"]').val();
    var wxID = "";
    $.ajax({
        url: "/checkCode",
        type: "post",
        data: {
            "code": code,
            "type": 'cic',
            "csrfmiddlewaretoken": csrftoken
        },
        success: function (data) {
            var res = JSON.parse(data);
            if (res.error)
                location.href = "/error"
            else if (res.wxID) {
                if (res.noBind) {
                    $("#continuedS").attr("disabled", true);
                }
                wxID = res.wxID
                $.ajax({
                    url: "/getCi",
                    type: "post",
                    data: {
                        "wxID": wxID,
                        "csrfmiddlewaretoken": csrftoken,
                    },
                    success: function (d) {
                        var r = JSON.parse(d);
                        if (r.zero == "0")
                            $("#zeroS").removeAttr("checked")
                        if (r.continued == "0")
                            $("#continuedS").removeAttr("checked")
                        $("#set").fadeToggle()
                    }
                })
            }
            else
                location.href = "/index"
        }
    });
    $("#save").click(function () {
        $("#bt_1").hide()
        $("#bt_2").show()
        var json = {
            "wxID": wxID,
            "csrfmiddlewaretoken": csrftoken,
        };
        json.zero = $("#zeroS").is(":checked");
        json.continued = $("#continuedS").is(":checked");
        $.ajax({
            url: "/ciSettings",
            type: "post",
            data: json,
            success: function (_data) {
                var _res = JSON.parse(_data);
                if (_res.OK) {
                    $("#bt_2").hide()
                    $("#bt_1").show()
                    $toast.fadeIn(100)
                    $toast.attr('aria-live', 'assertive')
                    setTimeout(function () {
                        $toast.fadeOut(100)
                        $toast.attr('aria-live', 'off')
                    }, 2000);
                }
            }
        })
    });

})