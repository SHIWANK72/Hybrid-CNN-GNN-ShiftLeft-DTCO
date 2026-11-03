// SPDX-License-Identifier: Apache-2.0
module alu(input clk, reset, input [15:0] a, b, input [2:0] op,
           output reg [15:0] result);
    reg [15:0] next_result;
    always @* begin
        case (op)
            0: next_result = a + b;
            1: next_result = a - b;
            2: next_result = a ^ b;
            3: next_result = a & b;
            4: next_result = a | b;
            5: next_result = a << b[3:0];
            6: next_result = a >> b[3:0];
            default: next_result = a < b ? 16'd1 : 16'd0;
        endcase
    end
    always @(posedge clk) begin
        if (reset) result <= 0;
        else result <= next_result;
    end
endmodule
