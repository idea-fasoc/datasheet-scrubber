
    $(document).ready(function() {
        // Setup - add a text input to each footer cell
        $('#dtBasicExample thead tr').clone(true).appendTo( '#dtBasicExample thead' );
        $('#dtBasicExample thead tr:eq(1) th').each( function (i) {
            var title = $(this).text();
            $(this).html( '<input type="text" placeholder="Search '+title+'" />' );     
            $( 'input', this ).on( 'keyup change', function () {
                if ( table.column(i).search() !== this.value ) {
                    table
                        .column(i)
                        .search( this.value )
                        .draw();
                }
            } );
        } );
     
        var table = $('#dtBasicExample').DataTable( {
            orderCellsTop: true,
            fixedHeader: true,
            pageLength: 50
        } );
    } );    