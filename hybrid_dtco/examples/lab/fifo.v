// SPDX-License-Identifier: Apache-2.0
module fifo(input clk, reset, push, pop, input [7:0] data_in,
            output [7:0] data_out, output empty, full);
    reg [7:0] memory [0:7];
    reg [2:0] read_pointer, write_pointer;
    reg [3:0] count;
    assign empty = count == 0;
    assign full = count == 8;
    assign data_out = memory[read_pointer];
    wire do_push = push && !full;
    wire do_pop = pop && !empty;
    always @(posedge clk) begin
        if (reset) begin read_pointer <= 0; write_pointer <= 0; count <= 0; end
        else begin
            if (do_push) begin
                memory[write_pointer] <= data_in;
                write_pointer <= write_pointer + 1'b1;
            end
            if (do_pop) read_pointer <= read_pointer + 1'b1;
            case ({do_push, do_pop})
                2'b10: count <= count + 1'b1;
                2'b01: count <= count - 1'b1;
                default: count <= count;
            endcase
        end
    end
endmodule
