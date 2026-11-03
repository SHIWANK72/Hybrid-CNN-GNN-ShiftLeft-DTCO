// SPDX-License-Identifier: Apache-2.0
module fir(input clk, reset, enable, input signed [11:0] sample,
           output reg signed [15:0] filtered);
    reg signed [11:0] d1, d2, d3;
    wire signed [15:0] x0 = {{4{sample[11]}}, sample};
    wire signed [15:0] x1 = {{4{d1[11]}}, d1};
    wire signed [15:0] x2 = {{4{d2[11]}}, d2};
    wire signed [15:0] x3 = {{4{d3[11]}}, d3};
    always @(posedge clk) begin
        if (reset) begin d1 <= 0; d2 <= 0; d3 <= 0; filtered <= 0; end
        else if (enable) begin
            d1 <= sample; d2 <= d1; d3 <= d2;
            filtered <= x0 + (x1 <<< 1) + (x2 <<< 1) + x3;
        end
    end
endmodule
