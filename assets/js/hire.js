var mouseShadow = {
    pointerX: 0,
    pointerY: 0,
    pageWidth: null,
    pageHeight: null,
    init: function() {
        this.cacheDom();
        this.setPageSize();
        this.bindEvents();
    },
    cacheDom: function() {
        this.$el = $('#name');
    },
    setPageSize: function() {
        this.pageWidth = $(document).width();
        this.pageHeight = $(document).height();
    },
    bindEvents: function() {
        $(document).on("mousemove", this.setPointerLocation.bind(this));
    },
    setPointerLocation: function() {
        this.pointerX = event.pageX;
        this.pointerY = event.pageY;
        this.logPointerLocation();
    },
    logPointerLocation: function() {
        console.log(this.pointerX + ',' + this.pointerY);
    },
    calculateShadow: function() {
        
    }
}
mouseShadow.init();
