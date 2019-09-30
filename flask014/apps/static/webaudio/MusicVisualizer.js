/**
 * Created by zhjm on 2017/12/11.
 */
function MusicVisualizer(obj) {
    //音频源节点对象:AudioBufferSourceNode
    this.bufferSource = null;
    //存放从服务器请求得到的原始的音频文件数据
    this.arrayBuffer = null;
    //解码后的音频数据:是个AudioBuffer对象
    this.decodedBuffer = null;
    //音频所处状态：loading,loaded,decoding,decoded, playing, paused, stop
    this.audioState = "stop";
    //暂停事件和播放事件被触发的关键时间节点
    this.startPlayTime = 0;
    this.pausePlayTime = 0;
    //第一次按下播放的时间节点
    this.firstPlayTime = 0;
    //累积暂停时间
    this.accumulatePauseTime = 0;
    //当前偏移量，即去除暂停时间的累计播放时间
    this.currentOffset = 0;
    //创建GainNode节点，调节音量
    this.gainNode = MusicVisualizer.audioCtx.createGain();
    //创建一个音频分析节点
    this.analyser = MusicVisualizer.audioCtx.createAnalyser();
    //设置音频分析节点参数
    this.visualDomian = obj.visual_domain;
    this.size = obj.size;
    this.analyser.fftsize = 2 * this.size;
    //把analyser节点连接到增益节点
    this.analyser.connect(this.gainNode);
    //把GainNode节点连接到DestinationNode上面
    this.gainNode.connect(MusicVisualizer.audioCtx.destination);
    //定义函数句柄，把一帧数据绘制在Canvas上
    this.drawMusicOnCanvas = obj.drawMusicOnCanvas;
}

//创建audio context对象，绑定到MusicVisualizer上去
MusicVisualizer.audioCtx = new (window.AudioContext || window.webkitAudioContext)();

//发送AJAX请求加载音频资源数据
MusicVisualizer.prototype.load = function (audio_url) {
    if (this.audioState != "stop") {
        alert('当前有音乐正在播放,请停止！');
        return
    }
    this.audioState = "loading";
    var xhr = new XMLHttpRequest();
    xhr.open("GET", audio_url);
    xhr.responseType = "arraybuffer";
    var self = this;
    xhr.onload = function () {
        self.arrayBuffer = xhr.response;
        alert('音乐加载成功！准备解码！');
        self.audioState = "loaded";
        self.decode();
    };
    xhr.send();
};

//解码音频数据
MusicVisualizer.prototype.decode = function () {
    if (this.audioState != "loaded") {
        alert("请等待音乐加载完毕！");
        return
    }
    this.audioState = "decoding";
    var self = this;
    MusicVisualizer.audioCtx.decodeAudioData(this.arrayBuffer, function (buffer) {
            self.decodedBuffer = buffer;
            alert('音频数据解码完毕,请播放！');
            self.audioState = "decoded";
        },
        function (err) {
            console.log(err)
        })
};

//播放音频数据
MusicVisualizer.prototype.play = function () {
    if (this.audioState == "playing")
        return;
    if (this.audioState == "stop" && this.decodedBuffer == null) {
        if (this.audioState != "decoded") {
            alert('请先加载并解码音乐！');
            return;
        }
    }
    this.bufferSource = MusicVisualizer.audioCtx.createBufferSource();
    this.bufferSource.buffer = this.decodedBuffer;
    this.bufferSource.connect(this.analyser);
    this.bufferSource.start(when = 0, offset = 0, duration = this.bufferSource.buffer.duration);
    this.audioState = "playing";
    this.startPlayTime = MusicVisualizer.audioCtx.currentTime;//本次开始播放的事件发生的绝对时间点
    this.firstPlayTime = MusicVisualizer.audioCtx.currentTime;
    //启动可视化
    this.visualize();

};

//加载并播放音频数据
MusicVisualizer.prototype.load_play = function (audio_url) {
    if (this.audioState != "stop") {
        alert('当前有音乐正在播放,请停止！');
        return
    }
    this.audioState = "loading";
    var xhr = new XMLHttpRequest();
    xhr.open("GET", audio_url);
    xhr.responseType = "arraybuffer";
    var self = this;
    xhr.onload = function () {
        self.arrayBuffer = xhr.response;
        alert('音乐加载成功！准备解码！');
        self.audioState = "loaded";
        MusicVisualizer.audioCtx.decodeAudioData(self.arrayBuffer, function (buffer) {
                self.decodedBuffer = buffer;
                alert('音频数据解码完毕,请播放！');
                self.audioState = "decoded";
                self.play();
            },
            function (err) {
                console.log(err)
            })
    };
    xhr.send();
};

//停止播放
MusicVisualizer.prototype.stop = function () {
    if (this.audioState == "playing") {
        this.bufferSource.stop();
        this.audioState = "stop";
        this.accumulatePauseTime = 0;
        //撤销动画
        window.cancelAnimationFrame(drawVisual);
    }
};

//暂停播放
MusicVisualizer.prototype.pause = function () {
    if (this.audioState == "playing") {
        this.bufferSource.stop();
        this.pausePlayTime = MusicVisualizer.audioCtx.currentTime;//本次暂停事件发生的绝对时间点
        this.audioState = "paused";
        //撤销动画
        window.cancelAnimationFrame(drawVisual);
    }
};

//继续播放
MusicVisualizer.prototype.continue = function () {
    if (this.audioState == "paused") {
        this.bufferSource = MusicVisualizer.audioCtx.createBufferSource();
        this.bufferSource.buffer = this.decodedBuffer;
        this.bufferSource.connect(this.analyser);
        pauseInterval = this.pausePlayTime - this.startPlayTime;//一次暂停时间间隔
        this.accumulatePauseTime += pauseInterval;//累积暂停时间
        this.bufferSource.start(when = 0, offset = this.accumulatePauseTime,
            duration = this.bufferSource.buffer.duration);
        this.startPlayTime = MusicVisualizer.audioCtx.currentTime;//本次开始播放的事件发生的绝对时间点
        this.audioState = "playing";
        //重启可视化过程
        this.visualize();
    }
};

//改变播放进度
MusicVisualizer.prototype.changeProgress = function (percent) {
    if (this.audioState == "playing") {
        this.stop();
        this.bufferSource = MusicVisualizer.audioCtx.createBufferSource();
        this.bufferSource.buffer = this.decodedBuffer;
        this.bufferSource.connect(this.analyser);
        duration = this.bufferSource.buffer.duration;//以秒为单位的歌曲长度
        this.bufferSource.start(when = 0, offset = duration * percent, duration = duration);
        this.startPlayTime = MusicVisualizer.audioCtx.currentTime;//本次开始播放的事件发生的绝对时间点
        this.audioState = "playing";
        //重启动画
        this.visualize();
    }
};

//调节音量
MusicVisualizer.prototype.changeVolumn = function (percent) {
    this.gainNode.gain.value = percent * percent;
};

//切换可视化域
MusicVisualizer.prototype.switchDomain = function (selecteddomian, size) {
    //撤销动画
    window.cancelAnimationFrame(drawVisual);
    //设置分析节点的参数
    this.visualDomian = selecteddomian;
    this.analyser.fftsize = 2 * size;
    //重新启动可视化过程
    this.visualize()
};

//负责逐帧调用analyser节点获取每一帧数据，把数据传递给DrawCanvas
MusicVisualizer.prototype.visualize = function () {
    if (this.audioState != "playing") {
        return;
    }
    //创建请求动画帧
    requestAnimationFrame = window.requestAnimationFrame ||
        window.webkitRequestAnimationFrame ||
        window.mozRequestAnimationFrame;
    var self = this;
    if (this.visualDomian == 'time') {
        // console.log("时域分析");
        //用于存放一帧的音频数据的数组
        var arr = new Uint8Array(this.analyser.fftsize);
        //负责获取并绘制一帧的数据
        function drawFrame() {
            //由 音频分析节点 获得 音频数据 数组
            self.analyser.getByteTimeDomainData(arr);
            //调用外部指定的可视化方法将数据画在canvas上
            self.drawMusicOnCanvas(arr);
            //获取当前累计播放时间
            self.currentOffset = self.getOffset();
            //循环调用，形成动画帧
            drawVisual = requestAnimationFrame(drawFrame);
        }

        //调用drawFrame，进入动画循环
        drawFrame();
    }
    if (this.visualDomian == 'frequency') {
        // console.log("频域分析");
        //用于存放一帧的音频数据的数组
        var arr = new Uint8Array(this.analyser.frequencyBinCount);
        //负责获取并绘制一帧的数据
        function drawFrame() {
            //由 音频分析节点 获得 音频数据 的 频率分量 数组
            self.analyser.getByteFrequencyData(arr);
            //调用外部指定的可视化方法将数据画在canvas上
            self.drawMusicOnCanvas(arr);
            //获取当前累计播放时间
            self.currentOffset = self.getOffset();
            //循环调用，形成动画帧
            drawVisual = requestAnimationFrame(drawFrame);
        }

        //调用drawFrame，进入动画循环
        drawFrame();
    }
};

//获取播放时间的偏移量(累计播放时长)
MusicVisualizer.prototype.getOffset = function () {
    return MusicVisualizer.audioCtx.currentTime - this.firstPlayTime - this.accumulatePauseTime;
};
