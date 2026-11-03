// SPDX-License-Identifier: Apache-2.0
module accumulator(input clk, reset, enable, input [31:0] data,
                   output reg [31:0] sum, output reg overflow);
    always @(posedge clk) begin
        if (reset) begin sum <= 0; overflow <= 0; end
        else if (enable) {overflow, sum} <= {1'b0, sum} + {1'b0, data};
    end
endmodule
