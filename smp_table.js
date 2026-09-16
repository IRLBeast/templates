new Vue({
  el: '#q-app',

  data() {
    return {
    loading: false,
    selectedRow: null,
    selectedMessageId: null,
    messageDialog: false,
    tableMode: "incoming",
    selectedOutMessageId: null,
    dbSchema: "BIKL",
    messageText: "",
      search: '',
      incomingColumns: [
    {name: "IdMessageInMX", label: "Идентификатор входного сообщения", field: "IdMessageInMX", sortable: true, align: "left"},
    {name: "IdMessageIn", label: "ИД входящего сообщения", field: "IdMessageIn", sortable: true},
    {name: "TmIn", label: "Время регистрации в журнале", field: "TmIn", sortable: true},
    {name: "CdErrorIn", label: "Код входного контроля", field: "CdErrorIn"},
    {name: "BizSvc", label: "Обозначение целевой бизнес-системы", field: "BizSvc"},
    {name: "BizMsgIdr", label: "Уникальный идентификатор бизнес-сообщения", field: "BizMsgIdr"},
    {name: "MsgDefIdr", label: "Тип сообщения", field: "MsgDefIdr"},
    {name: "NrBankSender", label: "Номер участника отправителя", field: "NrBankSender"},
    {name: "CdAuthSender", label: "Код аутентификации отправителя", field: "CdAuthSender"},
    {name: "NrBankReceiver", label: "Номер участника получателя", field: "NrBankReceiver"},
    {name: "CdAuthReceiver", label: "Код аутентификации получателя", field: "CdAuthReceiver"}
    ],
    outcomingColumns: [
    {name: "IdMessageOutMX", label: "Идентификатор исходящего сообщения", field: "IdMessageOutMX", sortable: true},
    {name: "TmOut", label: "Время регистрации в журнале", field: "TmOut", sortable: true},
    {name: "NrBankSender", label: "Номер участника отправителя", field: "NrBankSender"},
    {name: "CdAuthSender", label: "Код аутентификации отправителя", field: "CdAuthSender"},
    {name: "NrBankReceiver", label: "Номер участника получателя", field: "NrBankReceiver"},
    {name: "CdAuthReceiver", label: "Код аутентификации получателя", field: "CdAuthReceiver"},
    {name: "BizSvc", label: "Обозначение целевой бизнес-системы", field: "BizSvc"},
    {name: "BizMsgIdr", label: "Уникальный идентификатор сообщения", field: "BizMsgIdr"},
    {name: "MsgDefIdr", label: "Идентификатор определения сообщения", field: "MsgDefIdr"},
    {name: "IdMessageInMX", label: "Идентификатор входного сообщения", field: "IdMessageInMX"}
    ],
    adminColumns: [
    {name: "IdMessageGet", label: "Регистрационный номер сообщения", field: "IdMessageGet"},
    {name: "IdMsgSec", label: "Идентификатор сообщения", field: "IdMsgSec"},
    {name: "CdError", label: "Код ошибки", field: "CdError"},
    {name: "ClassMsg", label: "Класс сообщения", field: "ClassMsg"},
    {name: "TmCreate", label: "Дата создания сообщения", field: "TmCreate"},
    {name: "MsgText", label: "Текст сообщения", field: "MsgText"}
    ],

      data: [] };
  },
    mounted() {
    this.loadData();
},

methods: {

    attachContextMenu() {
    this.$nextTick(() => {
        const tbody = this.$el.querySelector("tbody");
        if (!tbody) {
            return;
        }
        if (tbody._contextMenuAttached) {
            return;
        }
        tbody._contextMenuAttached = true;
        tbody.addEventListener("contextmenu", (e) => {
            const tr = e.target.closest("tr");
            if (!tr) {
                return;
            }
            e.preventDefault();
            if (this.tableMode === "incoming") {
                this.selectedMessageId = tr.cells[0].innerText.trim();

            } else if (this.tableMode === "outgoing") {
                this.selectedOutMessageId = tr.cells[0].innerText.trim();

            } else if (this.tableMode === "admin") {
                this.selectedMessageId = tr.cells[0].innerText.trim();
            }

            this.$refs.rowMenu.show(e);
        });
    });
},

    getCellValue(row, col) {
    if (typeof col.field === "function") {
        return col.field(row);
    }
    return row[col.field];
    },

    openContextMenu(evt, row) {
    this.selectedRow = row;
    this.$refs.rowMenu.show(evt);
    },

    showMessage() {
    let url;

    if (this.tableMode === "incoming") {

        url = `/api/smp/message/${this.selectedMessageId}?schema=${this.dbSchema}`;

    } else if (this.tableMode === "outgoing") {

        url = `/api/smp/outgoing_message/${this.selectedOutMessageId}?schema=${this.dbSchema}`;

    } else {

        url = `/api/smp/message_admin/${this.selectedMessageId}?schema=${this.dbSchema}`;

    }

    fetch(url)
        .then(r => r.json())
        .then(data => {
            this.messageText = data.message;
            this.messageDialog = true;

            this.$nextTick(() => {
                this.$refs.xmlCode.textContent = this.messageText;
                hljs.highlightElement(this.$refs.xmlCode);
            });
        });
},


    loadData() {
    this.loading = true;

    fetch(`/api/smp/messages/?schema=${this.dbSchema}`)
        .then(response => response.json())
        .then(data => {
        this.data = data;
        this.attachContextMenu();
    })
        .finally(() => {
            this.loading = false;
        });
    },

    changeSchema() {
        this.tableMode = "incoming";
        this.loadData();
    },

    showOutgoing() {
    fetch(`/api/smp/outgoing/${this.selectedMessageId}?schema=${this.dbSchema}`)
        .then(r => r.json())
        .then(data => {
            this.data = data;
            this.tableMode = "outgoing";
            this.$nextTick(() => {
                this.attachContextMenu();
            });
        });
    },

    loadAdmin() {
    this.loading = true;
    fetch(`/api/smp/messages_admin?schema=${this.dbSchema}`)
        .then(r => r.json())
        .then(data => {
            this.data = data;
            this.tableMode = "admin";
            this.$nextTick(() => {
                this.attachContextMenu();
            });
        })
        .finally(() => {
            this.loading = false;
        });
    },

    loadIncoming() {
    this.tableMode = "incoming";
    this.loadData();
    },

}
   });