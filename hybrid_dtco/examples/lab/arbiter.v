// SPDX-License-Identifier: Apache-2.0
module arbiter(input clk, reset, input [31:0] request,
               output reg [31:0] grant, output reg valid);
    // Lowest-numbered asserted request wins. Bit isolation uses a carry chain.
    wire [31:0] selected = request & (~request + 32'd1);
    always @(posedge clk) begin
        if (reset) begin grant <= 0; valid <= 0; end
        else begin grant <= selected; valid <= |request; end
    end
endmodule
