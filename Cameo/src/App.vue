<template>
  <div>
    <el-container>
      <el-header style="text-align: right">
        <span style="font-size: 20px">Cameo字典翻译</span>
      </el-header>
      <div align="center">
        <el-tag v-text="blockName" style="margin: 10px; text-align: center; width: 40%">标签一</el-tag>
      </div>
      <el-main>
        <div align="center">
          <el-table
            ref="multipleTable"
            v-bind:data="tableData"
            border
            tooltip-effect="dark"
            style="width: 70%"
            size="medium"
            max-height="480px"
            @selection-change="handleSelectionChange"
          >
            <el-table-column fixed align="center" type="selection" width="75%"></el-table-column>
            <!-- <el-table-column align="center" label="日期" width="120">
            <template slot-scope="scope">{{ scope.row.date }}</template>
            </el-table-column>-->
            <el-table-column align="center" prop="origin" label="原始单词" show-overflow></el-table-column>
            <el-table-column align="center" prop="code" label="Cameo Code" width="100%"></el-table-column>
            <el-table-column align="center" prop="Chinese" label="翻译结果" show-overflow></el-table-column>
            <el-table-column align="center" prop="comment" label="注释（多为搭配的动词）" show-overflow></el-table-column>
          </el-table>
          <div style="margin-top: 20px">
            <el-button @click="end()">退出</el-button>
            <el-button :disabled="disableCommit" @click="sendData()">{{commit}}</el-button>
          </div>
        </div>
      </el-main>
      <el-footer>
        <div>
          <el-carousel
            style="width: 100%; margin: 10px"
            :autoplay="false"
            :interval="1"
            type="card"
            :height="refHeight"
          >
            <el-carousel-item v-for="item in cameoList" :key="item">
              <el-card :body-style="{ padding: '0px', overflow: 'scroll' }" class="box-card">
                <div slot="header" class="clearfix">
                  <span>Cameo 编号：{{item['code']}}</span>
                </div>
                <div style="margin:20px; overflow: scroll">
                  <b>Name:</b>
                  <ul class="text item">{{item['content']['name'] }}</ul>
                  <b>Description:</b>
                  <ul class="text item">{{ item['content']['description'] }}</ul>
                  <b>
                    <span v-if="item['content']['usage_notes'].length">Usage Notes:</span>
                  </b>
                  <ul class="text item">{{ item['content']['usage_notes'] }}</ul>
                  <b>
                    <span v-if="item['content']['example'].length">Example:</span>
                  </b>
                  <ul v-for="eg in item['content']['example']" :key="eg" class="text item">{{ eg }}</ul>
                </div>
              </el-card>
            </el-carousel-item>
          </el-carousel>
        </div>
      </el-footer>
    </el-container>
  </div>
</template>

<script>
export default {
  name: "App",
  data() {
    return {
      timer: null,
      commit: "确认",
      disableCommit: false,
      disableTime: 1,
      blockName: "Block Name",
      tableData: [],
      multipleSelection: [],
      cameoList: [],
      refHeight: "600px",
      screenWidth: document.body.clientWidth
    };
  },

  methods: {
    // toggleSelection(rows) {
    //   if (rows) {
    //     rows.forEach(row => {
    //       this.$refs.multipleTable.toggleRowSelection(row);
    //     });
    //   } else {
    //     this.$refs.multipleTable.clearSelection();
    //   }
    // },
    handleSelectionChange(val) {
      this.multipleSelection = val;
    },
    tempDisableCommit() {
      console.log("disable!");
      if (this.disableCommit) return;
      this.disableCommit = true;
      this.commit = this.disableTime + "s后可提交";
      let clock = window.setInterval(() => {
        --this.disableTime;
        console.log(this.disableTime);
        this.commit = this.disableTime + "s后可提交";
        if (this.disableTime < 0) {
          window.clearInterval(clock);
          this.commit = "确认";
          this.disableTime = 1;
          this.disableCommit = false;
        }
      }, 1000);
    },
    getData() {
      // console.log("????????SDDWQDASFADF");
      this.axios.get("/upload").then(response => this.setData(response.data));
    },
    setRefHeight() {
      var num = 0;
      // -margin*2 / num of cards to play(3) -left space / nums of charactors
      var charNum = ((this.screenWidth - 40) / 3 - 50) / 6;
      for (var i = 0; i < this.cameoList.length; ++i) {
        var exampleLen = 0;
        for (
          var j = 0;
          j < this.cameoList[0]["content"]["example"].length;
          ++j
        ) {
          exampleLen += this.cameoList[0]["content"]["example"][j].length;
        }
        console.log(exampleLen);
        var temp =
          62 +
          8 * 20 +
          (4 +
            Math.ceil(
              this.cameoList[0]["content"]["description"].length / charNum
            ) +
            Math.ceil(
              this.cameoList[0]["content"]["usage_notes"].length / charNum
            ) +
            Math.ceil(exampleLen / charNum)) *
            18 +
          this.cameoList[0]["content"]["example"].length * 20;
        if (temp > num) {
          num = temp;
        }
      }
      this.refHeight = num.toString() + "px";
      console.log(this.cameoList, this.refHeight);
    },
    setData(res) {
      // 若数据产生变化则刷新
      if (this.tableData.toString() == res["transData"].toString()) {
        // console.log("???????");
        return;
      }
      this.tableData = res["transData"];
      this.blockName = this.tableData[0]["class"];
      this.cameoList = res["cameoData"];

      this.setRefHeight();

      this.tempDisableCommit();
    },
    sendData() {
      console.log(this.multipleSelection);
      this.axios.post("/results", this.multipleSelection).then(response => {
        if (response.status == 0) {
          console.log("post succeed!");
        }
      });
    },
    end() {
      console.log("Try to send end signal...");
      this.axios.post("/end").then(response => {
        if (response.status == 0) {
          console.log("End succeed!");
        }
      });
    }
  },
  created() {
    this.getData();
    this.timer = setInterval(this.getData, 100); // 轮询数据
  },
  beforeDestroy() {
    clearInterval(this.timer);
  },
  mounted() {
    const that = this;
    window.onresize = () => {
      return (() => {
        window.screenWidth = document.body.clientWidth;
        that.screenWidth = window.screenWidth;
        this.setRefHeight();
      })();
    };
  }
};
</script>

<style>
/* #app {
  font-family: 'Avenir', Helvetica, Arial, sans-serif;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
  text-align: center;
  color: #2c3e50;
  margin-top: 60px;
} */
</style>
