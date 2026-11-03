"""CLI for packing, training, evaluating and demonstrating the lab prototype."""
import argparse
import json
from pathlib import Path


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)
    pack = commands.add_parser("pack")
    pack.add_argument("--corpus", required=True)
    pack.add_argument("--output", required=True)
    train = commands.add_parser("train")
    train.add_argument("--dataset", required=True)
    train.add_argument("--output", required=True)
    train.add_argument("--epochs", type=int, default=300)
    evaluate = commands.add_parser("evaluate")
    evaluate.add_argument("--dataset", required=True)
    evaluate.add_argument("--checkpoint", required=True)
    evaluate.add_argument("--output", required=True)
    predict = commands.add_parser("predict")
    predict.add_argument("--checkpoint", required=True)
    predict.add_argument("--graph", required=True)
    predict.add_argument("--clock-period", type=float, required=True)
    predict.add_argument("--utilization", type=float, required=True)
    predict.add_argument("--output", required=True)
    serve = commands.add_parser("serve")
    serve.add_argument("--checkpoint", required=True)
    serve.add_argument("--port", type=int, default=8000)
    args = parser.parse_args()
    if args.command == "pack":
        from hybrid_dtco.data.lab_dataset import pack_corpus

        result = pack_corpus(args.corpus, args.output)
        print(f"Packed {len(result['samples'])} samples")
    elif args.command == "train":
        if args.epochs < 1:
            parser.error("Epochs must be positive")
        from hybrid_dtco.train.trainer import train_lab

        print(
            json.dumps(
                train_lab(args.dataset, args.output, args.epochs)["selected"], indent=2
            )
        )
    elif args.command == "evaluate":
        from hybrid_dtco.train.evaluate import evaluate_lab

        print(
            json.dumps(
                evaluate_lab(args.dataset, args.checkpoint, args.output)["metrics"],
                indent=2,
            )
        )
    elif args.command == "predict":
        import torch

        torch.set_num_threads(2)
        from hybrid_dtco.api.predictor import LabPredictor

        graph = json.loads(Path(args.graph).read_text())
        prediction = LabPredictor(args.checkpoint).predict(
            graph, args.utilization, args.clock_period
        )
        with Path(args.output).open("x") as output:
            output.write(json.dumps(prediction, indent=2) + "\n")
        print(f"Prediction written to {args.output}")
    else:
        import torch
        import uvicorn
        from hybrid_dtco.api.server import create_app

        torch.set_num_threads(2)
        uvicorn.run(create_app(args.checkpoint), host="127.0.0.1", port=args.port)


if __name__ == "__main__":
    main()
