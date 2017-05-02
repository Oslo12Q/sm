$(function() {
    var table_str = "";
    var table_header = "";
    var table_th = "";
    var h3;
    var dataFor;
    var fileArea = $(".fileArea");
    var upLoadImg = document.createElement('img');
    function urlData() {
        var url = location.search;
        var newURL = url.split('?')
        for (var i = 0; i < newURL.length; i++) {
            var index = newURL[i].indexOf('=');
            if (index != -1) {
                return newURL[i].substr(index + 1);
            }
        }
    }
    fileChange();

    function fileChange() {
        $('.fileUpload').change(function() {
            var file = this.files[0];
            var fileType = file.type;
            var fileSize = file.size;
            var filename = file.name;
            var reader = new FileReader();
            reader.readAsDataURL(file);
            if(fileType.indexOf('image')==-1){
                showInfo('文件格式有误');
                return;
            }
            if(fileSize>=10485760){
                showInfo('上传文件太大！');
                return;
            }
            reader.onload = function() {
                var base64 = this.result;
                var imgClassify = urlData();
                upLoadImg.src = base64;
                $('.showPreView').append(upLoadImg);
                $('.upLoadFile').hide();
                var baseStr=base64.substr(23);
                $('.upInfo').fadeIn();
                 $.ajax({
                    url: '/id_card/async_analysis/',
                    type: 'POST',
                    data: {fileData:baseStr},
                    success: function(msg) {
                        var file_id = msg.data.fid;
                        get_ocr_result(file_id);
                    }
                })
            }

        })
    };

    function showInfo(infoText){
        $('.info').fadeIn().html(infoText);
        setTimeout(function(){
            $('.info').hide().html('');
        }, 1000)
    };
        
   function get_ocr_result(fid) {
        var url = '/id_card/async_analysis/result/?fid=' + fid + '&type=info';
        $.get(url, function(data) {
            var stringJson=JSON.stringify(data);
                if (data.status == 'error') {
                    return;
                }
                if (data.status == 'running') {
                    setTimeout(function() {
                        get_ocr_result(fid); 
                    }, 1000);
                    return;
                }
                if (data.status == '500') {
                    $('.upInfo>span').html('无法正常识别！');
                    return;
                }
                var info_name,
                info_sex,
                info_ads,
                info_minzu,
                info_number,
                info_br;

                $.ajax({
                    url:'./id_cart.json',
                    timeout:1,
                    success:function(msg){
                        $('.info_name').html(msg['姓名'])
                        $('.info_sex').html(msg['性别'])
                        $('.info_ads').html(msg['住址'])
                        $('.info_minzu').html(msg['民族'])
                        $('.info_number').html(msg['公民身份号码'])
                        $('.info_br').html(msg['出生'])
                        $('.info_c').html(msg['参考地址'])
                    }
                })
                $('.mainTable').fadeIn();
                $('.upInfo>span').html('识别完成!');
        });
    }

})
