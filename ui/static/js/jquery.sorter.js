/**
 * jQuery Element Sorter 1.1
 *
 * http://plugins.jquery.com/project/ElementSort
 *
 */

(function($){
    $.fn.extend({

        sort: function(params) {

        //expected params
        /*
        {
            sortOn: '.selector',  //selector of the column to sort on
            direction: 'asc' | 'desc' //optional..defaults to asc
            sortType: 'string | date | number' //optional..defaults to string
        }

        OR

        an array of the above obj for multi sorting. The order in the array determines
        order of precedence
        */

            //hacky to be backward compatible
            if(!params.length)
            {
                params = [params];
            }

            var sortFunc = function(a, b)
            {
                var retval;
                var typedData;

                for(var i = 0;i<params.length;i++)
                {
                    typedData = getTypedData(a, b, i);
                    retval = innerSort(typedData.a, typedData.b, params[i].direction);
                    if(retval != 0)
                      break;
                }
                return retval;
            }

            var getTypedData = function(a, b, index)
            {
                var sortType = params[index].sortType;
                var preA, preB;
                var typedA, typedB;

                preA = getValue(a, index);
                preB = getValue(b, index);
                if(sortType == 'date')
                {
                    typedA = new Date(Date.parse(preA));
                    typedB = new Date(Date.parse(preB));
                }
                else if(sortType == 'number')
                {
                    typedA = new Number(preA);
                    typedB = new Number(preB);
                }
                else
                {
                    typedA = new String(preA).toLowerCase();
                    typedB = new String(preB).toLowerCase();
                }
                return {a: typedA, b: typedB};
            }

            var getValue = function(obj, index)
            {
                var val;
                if(obj.hash[index])
                {
                    val = obj.hash[index];
                }
                else
                {
                    val = findValue(obj.row, params[index].sortOn);
                    obj.hash[index] = val;
                }
                return val;
            }

            var findValue = function(row, selector)
            {
                return row.find(selector).text();
            }

            var innerSort = function(a, b, direction)
            {
                var retval;
                if(a > b)
                {
                    retval = 1;
                }
                else if(a < b)
                {
                    retval = -1;
                }
                else
                {
                    retval = 0;
                }
                if(direction == 'desc')
                    retval*=-1;
                return retval;
            }

            var getRowHash = function(rows)
            {
                var rowHash = [];
                for(var x = 0;x < rows.length;x++)
                {
                    rowHash[x] = {row: $(rows[x]), hash: []};
                }
                return rowHash;
            }

            var addRows = function(container, rowHash)
            {
                var c = $('<div></div>');
                for(var x = 0; x < rowHash.length; x++)
                {
                    c.append(rowHash[x].row);
                }
                container.append(c.children());
            }

            return this.each(function() {
                var container = $(this);
                var rows = container.children();

                var rowHash = getRowHash(rows);

                rowHash.sort(sortFunc);


                addRows(container, rowHash);

            });

        }
    });
})(jQuery);