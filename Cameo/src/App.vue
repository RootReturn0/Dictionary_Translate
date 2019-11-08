<template>
  <div>
    <el-container>
      <el-header style="text-align: right">
        <span style="font-size: 20px">Cameo字典翻译</span>
      </el-header>
      <div align="center">
        <el-tag  v-text="blockName" style="margin: 10px; text-align: center; width: 40%">标签一</el-tag>
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
            @selection-change="handleSelectionChange"
          >
            <el-table-column align="center" type="selection" width="75%"></el-table-column>
            <!-- <el-table-column align="center" label="日期" width="120">
            <template slot-scope="scope">{{ scope.row.date }}</template>
            </el-table-column>-->
            <el-table-column align="center" prop="origin" label="原始单词" show-overflow-tooltip></el-table-column>
            <el-table-column align="center" prop="code" label="Cameo Code" width="100%"></el-table-column>
            <el-table-column align="center" prop="Chinese" label="翻译结果" show-overflow-tooltip></el-table-column>
          </el-table>
          <div style="margin-top: 20px">
            <el-button @click="end()">退出</el-button>
            <el-button @click="sendData()">确认</el-button>
          </div>
        </div>
      </el-main>
    </el-container>
  </div>
</template>

<script>
export default {
  name: "App",
  data() {
    return {
      blockName: "Block Name",
      tableData: [],
      multipleSelection: []
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
    getData() {
      console.log("????????SDDWQDASFADF");
      this.axios
        .get("/upload")
        .then(
          response => (
            console.log(response),
            ((this.tableData = response.data),
            (this.blockName = response.data[0]["class"]))
          )
        );
    },
    sendData() {
      console.log(this.multipleSelection)
        this.axios.post("/results", this.multipleSelection).then(response => {
          if (response.status == 0) {
            console.log("post succeed!");
          }
        });

      this.reload();
    },
    end(){
        console.log('Try to send end signal...')
        this.axios.post("/end").then(response=>{
            if (response.status == 0) {
            console.log("End succeed!");
          }
        })
    },
    reload() {
        this.getData();
        this.$forceUpdate();
        }
  },
  created() {
    this.getData();
  },
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
