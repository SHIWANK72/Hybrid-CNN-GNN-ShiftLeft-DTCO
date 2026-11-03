"""Small GraphSAGE encoder for the bounded laboratory prototype."""
from torch import nn
from torch_geometric.nn import SAGEConv


class GraphEncoder(nn.Module):
    def __init__(self, in_channels, hidden_channels):
        super().__init__()
        self.first = SAGEConv(in_channels, hidden_channels)
        self.second = SAGEConv(hidden_channels, hidden_channels)

    def forward(self, x, edge_index):
        return self.second(self.first(x, edge_index).relu(), edge_index).relu()
